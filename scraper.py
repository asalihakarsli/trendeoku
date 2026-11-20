import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from pathlib import Path
from urllib.parse import urljoin

# Ayarlar
BASE_URL = "https://katalog.ankara.bel.tr"
SEARCH_URL = "https://katalog.ankara.bel.tr/cgi-bin/koha/opac-search.pl?idx=&q=&limit=branch%3AYHT"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}
KONUM_SABIT = "Ankara YHT Gar Kütüphanesi"
OKUMA_HIZI = 40  # Saatte okunan sayfa sayısı
ISLEMLER_ARASI_BEKLEME = 2.5  # Sunucuyu yormamak için istekler arası bekleme (sn)
VERI_KLASORU = Path(__file__).resolve().parent / "data"
CIKTI_DOSYASI = VERI_KLASORU / "gar_kutuphanesi_veriseti.csv"

oturum = requests.Session()
oturum.headers.update(HEADERS)


def guvenli_istek(url, timeout=30, maks_deneme=5):
    """503/429/502/504 gibi geçici sunucu hatalarında artan sürelerle bekleyip tekrar dener."""
    gecici_hatalar = {429, 500, 502, 503, 504}

    for deneme in range(1, maks_deneme + 1):
        try:
            yanit = oturum.get(url, timeout=timeout)
            if yanit.status_code in gecici_hatalar:
                bekleme = 15 * (2 ** (deneme - 1))  # 15s, 30s, 60s, 120s, 240s
                print(
                    f"  ⏳ Sunucu {yanit.status_code} yanıtı verdi "
                    f"(Deneme {deneme}/{maks_deneme}). {bekleme} saniye beklenip devam edilecek..."
                )
                time.sleep(bekleme)
                continue

            yanit.raise_for_status()
            return yanit

        except requests.exceptions.RequestException as e:
            if deneme == maks_deneme:
                print(f"  ❌ {maks_deneme} deneme sonunda istek başarısız oldu: {e}")
                return None
            bekleme = 15 * (2 ** (deneme - 1))
            print(
                f"  ⏳ Bağlantı/sunucu hatası ({e}) - "
                f"Deneme {deneme}/{maks_deneme}. {bekleme} saniye bekleniyor..."
            )
            time.sleep(bekleme)

    return None


def ozeti_kisalt(metin, max_cumle=4):
    """Uzun kitap özetlerini anlam bütünlüğünü bozmadan 3-5 cümleye indirger."""
    if not metin:
        return None
    temiz = re.sub(r"\s+", " ", metin).strip()
    temiz = re.sub(r"^(Özet|Tanıtım Yazısı|Konu)\s*:\s*", "", temiz, flags=re.IGNORECASE)

    cumleler = re.split(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ\"'“])", temiz)
    cumleler = [c.strip() for c in cumleler if c.strip()]

    if len(cumleler) <= max_cumle:
        return " ".join(cumleler)

    secilen = cumleler[:max_cumle]
    if len(" ".join(secilen)) < 220 and len(cumleler) >= 5:
        secilen = cumleler[:5]

    return " ".join(secilen)


def gorsel_bul(detay_soup):
    """Koha detay sayfasından kapak görseli URL'sini bulur."""
    seciciler = [
        "#bookcover img",
        ".bookcover img",
        ".coverimages img",
        "img[src*='opac-image.pl']",
        "img[src*='cover']",
    ]
    for secici in seciciler:
        img = detay_soup.select_one(secici)
        if img and img.get("src"):
            src = img["src"].strip()
            if "blank" in src.lower() or "noimage" in src.lower() or src.startswith("data:"):
                continue
            return urljoin(BASE_URL, src)

    isbn_etiketi = detay_soup.select_one("span[property='isbn'], .results_summary.isbn")
    if isbn_etiketi:
        isbn_temiz = re.sub(r"[^0-9Xx]", "", isbn_etiketi.text)
        if len(isbn_temiz) in (10, 13):
            return f"https://covers.openlibrary.org/b/isbn/{isbn_temiz}-M.jpg?default=false"

    return None


def ozet_bul(detay_soup):
    """Koha MARC 520 özet alanından veya açıklama sekmelerinden özet metnini çeker."""
    seciciler = [
        ".results_summary.summary",
        "#descriptions .content_set",
        "#descriptions",
        "span[property='summary']",
        ".summary",
    ]
    for secici in seciciler:
        etiket = detay_soup.select_one(secici)
        if etiket:
            metin = etiket.get_text(" ", strip=True)
            if len(metin) > 30:
                return ozeti_kisalt(metin)
    return None


def detay_sayfasini_tara(url):
    """Kitabın içine girerek Yazar, Dil, Sayfa Sayısı, Görsel ve Özet bilgilerini çeker."""
    bilgiler = {
        "Yazar": None,
        "Dil": None,
        "Sayfa Sayısı": 0,
        "Gorsel": None,
        "Ozet": None,
    }

    req = guvenli_istek(url, timeout=30)
    if req is None:
        return bilgiler

    detay_soup = BeautifulSoup(req.content, "html.parser")

    # 1. Yazar Çekme
    yazar_etiketi = detay_soup.find("h5", class_="author")
    if not yazar_etiketi:
        yazar_etiketi = detay_soup.select_one(".results_summary.author a")
    if yazar_etiketi:
        bilgiler["Yazar"] = yazar_etiketi.text.strip()

    # 2. Dil Çekme
    dil_etiketi = detay_soup.find("span", class_="results_summary language")
    if dil_etiketi:
        dil_degeri_etiketi = dil_etiketi.find("span", class_="language")
        if dil_degeri_etiketi:
            bilgiler["Dil"] = dil_degeri_etiketi.text.strip()

    # 3. Sayfa Sayısı Çekme
    tanim_etiketi = detay_soup.find("span", property="description")
    if tanim_etiketi:
        tanim_metni = tanim_etiketi.text.strip()
        sayfa_bul = re.search(r"(\d+)\s*sayfa", tanim_metni, re.IGNORECASE)
        if sayfa_bul:
            bilgiler["Sayfa Sayısı"] = int(sayfa_bul.group(1))

    # 4. Kapak Görseli ve 5. Özet Çekme
    bilgiler["Gorsel"] = gorsel_bul(detay_soup)
    bilgiler["Ozet"] = ozet_bul(detay_soup)

    return bilgiler


def mevcut_veriyi_yukle():
    """Varsa önceki CSV dosyasını okur; mevcut satırları ve görülen linkleri döndürür."""
    if not CIKTI_DOSYASI.exists():
        return [], set()

    df_eski = pd.read_csv(CIKTI_DOSYASI)
    eski_kayitlar = df_eski.to_dict(orient="records")
    gorulen_linkler = {
        str(r["Link"]).strip()
        for r in eski_kayitlar
        if pd.notna(r.get("Link"))
    }
    return eski_kayitlar, gorulen_linkler


def veriyi_kaydet(mevcut_kayitlar, yeni_kitaplar):
    """Toplanan verileri CSV dosyasına güvenli şekilde kaydeder."""
    tum_kayitlar = mevcut_kayitlar + yeni_kitaplar
    df = pd.DataFrame(tum_kayitlar)
    if df.empty:
        return df

    df["Sayfa Sayısı"] = pd.to_numeric(df["Sayfa Sayısı"], errors="coerce").astype("Int64")
    VERI_KLASORU.mkdir(parents=True, exist_ok=True)
    df.to_csv(CIKTI_DOSYASI, index=False, encoding="utf-8-sig")
    return df


def sure_araliginda_kitap_ekle(hedef_yeni_kitap=30, min_okuma_saati=0.1, maks_okuma_saati=2.7):
    """Mevcut veri setini koruyarak, okuma süresi belirtilen aralıkta olan yeni kitapları ekler."""
    maks_sayfa = int(maks_okuma_saati * OKUMA_HIZI)  # 2.7 * 40 = 108 sayfa
    mevcut_kayitlar, gorulen_linkler = mevcut_veriyi_yukle()
    yeni_kitaplar = []
    sayfa_offset = 0

    print(f"Mevcut veri setinde {len(mevcut_kayitlar)} kitap korunuyor.")
    print(
        f"Hedef: Okuma süresi {maks_okuma_saati} saat ve altında "
        f"(<= {maks_sayfa} sayfa) olan {hedef_yeni_kitap} yeni kitap eklemek...\n"
    )

    while len(yeni_kitaplar) < hedef_yeni_kitap:
        guncel_sayfa_url = f"{SEARCH_URL}&offset={sayfa_offset}"
        response = guvenli_istek(guncel_sayfa_url, timeout=20)

        if response is None:
            print("\n⚠️ Arama sayfasına ulaşılamadı, şimdiye kadar toplanan veriler kaydediliyor...")
            break

        soup = BeautifulSoup(response.content, "html.parser")
        kitap_linkleri = soup.select("a.title")

        if not kitap_linkleri:
            print("\nKütüphanedeki tüm katalog tarandı, başka sonuç kalmadı.")
            break

        for link_etiketi in kitap_linkleri:
            if len(yeni_kitaplar) >= hedef_yeni_kitap:
                break

            detay_url = BASE_URL + link_etiketi["href"]

            # Zaten veri setinde kayıtlı olan veya bu turda kontrol edilen kitapları atla
            if detay_url in gorulen_linkler:
                continue

            gorulen_linkler.add(detay_url)

            tam_baslik = link_etiketi.text.strip()
            kitap_adi = tam_baslik.split(" / ")[0].strip() if " / " in tam_baslik else tam_baslik

            detay_bilgileri = detay_sayfasini_tara(detay_url)
            sayfa = detay_bilgileri["Sayfa Sayısı"]

            if not isinstance(sayfa, int) or sayfa <= 0 or sayfa > maks_sayfa:
                print(f"  [Atlandı - {sayfa if sayfa > 0 else '?'} sf] {kitap_adi}")
                time.sleep(ISLEMLER_ARASI_BEKLEME)
                continue

            okuma_suresi = round(sayfa / OKUMA_HIZI, 1)
            if okuma_suresi < min_okuma_saati or okuma_suresi > maks_okuma_saati:
                print(f"  [Atlandı - {okuma_suresi} sa] {kitap_adi}")
                time.sleep(ISLEMLER_ARASI_BEKLEME)
                continue

            satir = {
                "Kitap Adı": kitap_adi,
                "Yazar": detay_bilgileri["Yazar"],
                "Kitap Dili": detay_bilgileri["Dil"],
                "Sayfa Sayısı": sayfa,
                "Tahmini Okunma Süresi (Saat)": okuma_suresi,
                "Konum": KONUM_SABIT,
                "Link": detay_url,
                "Görsel": detay_bilgileri["Gorsel"],
                "Özet": detay_bilgileri["Ozet"],
            }

            yeni_kitaplar.append(satir)
            veriyi_kaydet(mevcut_kayitlar, yeni_kitaplar)

            print(
                f"✅ [{len(yeni_kitaplar)}/{hedef_yeni_kitap}] Eklendi ve kaydedildi: "
                f"{kitap_adi} ({sayfa} sayfa / {okuma_suresi} saat)"
            )
            time.sleep(ISLEMLER_ARASI_BEKLEME)

        sayfa_offset += 20
        time.sleep(ISLEMLER_ARASI_BEKLEME)

    df = veriyi_kaydet(mevcut_kayitlar, yeni_kitaplar)
    if df.empty:
        print("Hiç kitap verisi toplanamadı, dosya yazılmadı.")
        return df

    print(
        f"\n🎉 İşlem Tamamlandı! {len(yeni_kitaplar)} yeni kitap eklendi. "
        f"Toplam kitap sayısı: {len(df)} -> '{CIKTI_DOSYASI}'"
    )
    return df
