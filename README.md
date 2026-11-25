# Ankara Train Book Recommender (Trende Ne Okusam?)

*Picks single books or multi-book reading bundles from the Ankara YHT Station Library catalog that fit the length of your train journey from Ankara — including Turistik Tren routes, return points, and an admin catalog manager. Python, web scraping, pandas, HTML/CSS/JS.*

Ankara Büyükşehir Belediyesi'nin **Ankara YHT Gar Kütüphanesi** kataloğundan kitap bilgilerini, kapak görsellerini ve özetlerini toplar (`scraper.py`); seçtiğiniz şehre olan tren yolculuğunuzun süresine göre okuyabileceğiniz kitapları hem komut satırında (`recommender.py`) hem de statik web arayüzünde (`site/index.html`) önerir[cite: 25].

## Öne Çıkan Özellikler

* **Tek Yön & Gidiş-Dönüş ve Çift Yönlü Güzergah:** Ankara çıkışlı veya Ankara varışlı (Nereden / Nereye yön değiştirme butonlu) tek yön ve gidiş-dönüş yolculuk sürelerini otomatik hesaplar.
* **Turistik Tren Modu:** Standart YHT ve konvansiyonel hatların (Eskişehir, Konya, Sivas, Karaman, İstanbul, Kayseri, Adana, İzmir, Erzurum, Diyarbakır, Kars) yanı sıra **Turistik Tren** (Turistik Doğu Ekspresi, Diyarbakır Ekspresi, Tatvan Treni, Karaelmas Ekspresi, Tuz Ekspresi) rotalarını kış temasıyla sunar.
* **Çoklu Kitap Önerisi (Yeşil Çerçeve Sistemi):** Kars (26 saat), Turistik Doğu Ekspresi (32 saat) veya gidiş-dönüş gibi tek bir kitabın süreyi doldurmaya yetmediği uzun yolculuklarda, yolculuk süresini en verimli dolduran **2–4 kitaplık okuma paketlerini** yeşil çerçeve ve üst bilgilendirme kutusuyla öne çıkarır.
* **İade Noktası ve Harita Yönlendirmesi:** Konya rotası seçildiğinde kütüphane iade noktası adresini (*Konevi, Alay Cd. No:9, 42040 Meram/Konya*) ve doğrudan Google Haritalar yol tarifi bağlantısını gösterir.
* **Zengin Kitap Kartları:** Kitap kapak görselleri (eksik kapaklar için otomatik tipografik kapak tasarımı), 3–5 cümlelik özetler, okunma yüzdesi çubuğu ve katalog bağlantıları yer alır.
* **Tarayıcı Tabanlı Admin Paneli & Beni Oku Sekmesi:** Web arayüzü üzerinden CSV/JSON dosyası yükleme, tekil kitap ekleme/silme, güncel `kitaplar.json` çıktısını indirme ve proje dokümantasyonunu görüntüleme imkânı sunar.

## Nasıl Çalışır?

1. **Veri Toplama (`scraper.py`):** Ankara Büyükşehir Belediyesi Koha kütüphane kataloğundaki YHT Gar Kütüphanesi kayıtlarını tarayarak kitabın adını, yazarını, dilini, sayfa sayısını, kapak görselini ve 3–5 cümlelik kısaltılmış özetini toplar[cite: 25]. Okunma süresi, sayfa sayısının sabit bir okuma hızına (**saatte 40 sayfa**) bölünmesiyle hesaplanır[cite: 25].
2. **Web Verisi Üretimi (`build_json.py`):** Toplanan `data/gar_kutuphanesi_veriseti.csv` dosyasını web arayüzünün okuyabileceği `site/kitaplar.json` formatına dönüştürür[cite: 25].
3. **Öneri Motoru (`recommender.py` & `site/index.html`):** Seçilen rotanın yolculuk süresine sığan kitapları süreyi en iyi dolduranlardan başlayarak sıralar[cite: 25]. Tek bir kitap sürenin %85'ini dolduramıyorsa birlikte bitirilebilecek çoklu kitap kombinasyonları oluşturur.

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### 1. Veri setini güncelleme (İsteğe bağlı)

```bash
python scraper.py        # veriyi toplar / günceller -> data/gar_kutuphanesi_veriseti.csv
python build_json.py     # CSV verisini web için JSON'a çevirir -> site/kitaplar.json
```

*(Alternatif olarak web arayüzündeki **Admin** sekmesinden güncel CSV veya JSON dosyanızı doğrudan yükleyip `kitaplar.json` olarak dışa aktarabilirsiniz.)*

### 2. Komut satırından (CLI) öneri alma

```bash
python recommender.py
```

### 3. Web arayüzünü çalıştırma

`site/index.html` dosyası `fetch("kitaplar.json")` ile veri çektiği için yerel bir HTTP sunucusu üzerinden açılmalıdır[cite: 25]:

```bash
python -m http.server 8000 --directory site
```

Ardından tarayıcınızda `http://localhost:8000` adresine gidebilirsiniz[cite: 25].

### 4. Birim testlerini çalıştırma

```bash
pytest
```

## Proje Yapısı

```text
├── scraper.py                         katalogdan kapak ve özet dahil veri toplar
├── build_json.py                      CSV verisini site/kitaplar.json'a dönüştürür
├── recommender.py                     komut satırı (CLI) öneri programı
├── tests/
│   └── test_recommender.py            otomatik birim testleri (pytest)
├── data/
│   └── gar_kutuphanesi_veriseti.csv   katalog veri seti
├── site/
│   ├── index.html                     statik web arayüzü (Ana Sayfa, Beni Oku, Admin)
│   └── kitaplar.json                  web arayüzü için üretilen kitap verisi
├── requirements.txt                   Python bağımlılıkları
├── README.md                          proje dokümantasyonu
└── .gitignore                         Git tarafından yoksayılacak dosyalar
```
