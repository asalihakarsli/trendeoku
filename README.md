# Ankara Train Book Recommender (Trende Ne Okusam?)

*Picks single books or multi-book reading bundles from the Ankara YHT Station Library catalog that fit the length of your train journey from Ankara — including Turistik Tren routes, return points, and an admin catalog manager. Python, web scraping, pandas, HTML/CSS/JS.*

Ankara Büyükşehir Belediyesi'nin **Ankara YHT Gar Kütüphanesi** kataloğundan kitap bilgilerini, kapak görsellerini ve özetlerini toplar (`scraper.py`); seçtiğiniz şehre olan tren yolculuğunuzun süresine göre okuyabileceğiniz kitapları hem komut satırında (`recommender.py`) hem de zengin özellikli statik web arayüzünde (`site/index.html`) önerir[cite: 23, 24, 26, 27, 30].

## Öne Çıkan Özellikler

* **Tek Yön & Gidiş-Dönüş ve Çift Yönlü Güzergah:** Ankara çıkışlı veya Ankara varışlı (Nereden / Nereye yön değiştirme butonlu) tek yön ve gidiş-dönüş yolculuk sürelerini otomatik hesaplar.
* **Turistik Tren Modu:** Standart YHT ve konvansiyonel hatların (Eskişehir, Konya, Sivas, Karaman, İstanbul, Kayseri, Adana, İzmir, Erzurum, Diyarbakır, Kars) yanı sıra **Turistik Tren** (Turistik Doğu Ekspresi, Diyarbakır Ekspresi, Tatvan Treni, Karaelmas Ekspresi, Tuz Ekspresi) rotalarını kış temasıyla sunar[cite: 24, 27].
* **Çoklu Kitap Önerisi (Yeşil Çerçeve Sistemi):** Kars (26 saat), Turistik Doğu Ekspresi (32 saat) veya gidiş-dönüş gibi tek bir kitabın süreyi doldurmaya yetmediği uzun yolculuklarda, yolculuk süresini en verimli dolduran **2–4 kitaplık okuma paketlerini** yeşil çerçeve ve üst bilgilendirme kutusuyla öne çıkarır[cite: 27, 28].
* **İade Noktası ve Harita Yönlendirmesi:** Konya rotası seçildiğinde kütüphane iade noktası adresini (*Konevi, Alay Cd. No:9, 42040 Meram/Konya*) ve doğrudan Google Haritalar yol tarifi bağlantısını gösterir.
* **Zengin Kitap Kartları:** Kitap kapak görselleri (eksik kapaklar için otomatik tipografik kapak tasarımı), 3–5 cümlelik özetler, okunma yüzdesi çubuğu ve katalog bağlantıları yer alır[cite: 26, 27].
* **Tarayıcı Tabanlı Admin Paneli & Beni Oku Sekmesi:** Web arayüzü üzerinden CSV/JSON dosyası yükleme, tekil kitap ekleme/silme, güncel `kitaplar.json` çıktısını indirme ve proje dokümantasyonunu görüntüleme imkânı sunar[cite: 27].

## Nasıl Çalışır?

1. **Veri Toplama (`scraper.py`):** Ankara Büyükşehir Belediyesi Koha kütüphane kataloğundaki YHT Gar Kütüphanesi kayıtlarını tarayarak kitabın adını, yazarını, dilini, sayfa sayısını, kapak görselini ve 3–5 cümlelik kısaltılmış özetini toplar[cite: 26]. Okunma süresi, sayfa sayısının sabit bir okuma hızına (**saatte 40 sayfa**) bölünmesiyle hesaplanır ve mevcut veri setini koruyarak belirli saat aralıklarında yeni kitaplar ekleyebilir[cite: 26].
2. **Web Verisi Üretimi (`build_json.py`):** Toplanan `data/gar_kutuphanesi_veriseti.csv` dosyasını web arayüzünün okuyabileceği `site/kitaplar.json` formatına dönüştürür[cite: 23].
3. **Öneri Motoru (`recommender.py` & `site/index.html`):** Seçilen rotanın yolculuk süresine sığan kitapları süreyi en iyi dolduranlardan başlayarak sıralar[cite: 24, 27]. Tek bir kitap sürenin %85'ini dolduramıyorsa birlikte bitirilebilecek çoklu kitap kombinasyonları oluşturur[cite: 27].

## Kurulum

```bash
pip install -r requirements.txt
