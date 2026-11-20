"""data/gar_kutuphanesi_veriseti.csv dosyasını site/kitaplar.json'a çevirir.

scraper.py ile veriyi yeniledikten sonra bir kez çalıştırın:  python build_json.py
"""
import json
from pathlib import Path
import pandas as pd

KOK = Path(__file__).resolve().parent
SURE = "Tahmini Okunma Süresi (Saat)"

df = pd.read_csv(KOK / "data" / "gar_kutuphanesi_veriseti.csv")
df[SURE] = pd.to_numeric(df[SURE], errors="coerce")
df = df[df[SURE] > 0]

kitaplar = []
for _, r in df.iterrows():
    kayit = {
        "ad": str(r["Kitap Adı"]).strip(),
        "yazar": str(r["Yazar"]).strip() if pd.notna(r["Yazar"]) else "",
        "dil": str(r["Kitap Dili"]).strip() if pd.notna(r["Kitap Dili"]) else "TR",
        "sayfa": int(r["Sayfa Sayısı"]),
        "sure": float(r[SURE]),
        "link": str(r["Link"]).strip() if pd.notna(r["Link"]) else "",
        "gorsel": str(r["Görsel"]).strip() if "Görsel" in df.columns and pd.notna(r["Görsel"]) else "",
        "ozet": str(r["Özet"]).strip() if "Özet" in df.columns and pd.notna(r["Özet"]) else "",
    }
    kitaplar.append(kayit)

cikti = KOK / "site" / "kitaplar.json"
cikti.write_text(json.dumps(kitaplar, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(kitaplar)} kitap yazıldı -> {cikti}")
