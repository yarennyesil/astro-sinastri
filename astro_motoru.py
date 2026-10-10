import swisseph as swe

BURCLAR = [
    "Koç", "Boğa", "İkizler", "Yengeç", 
    "Aslan", "Başak", "Terazi", "Akrep", 
    "Yay", "Oğlak", "Kova", "Balık"
]

GEZEGENLER = {
    "Güneş": swe.SUN,
    "Ay": swe.MOON,
    "Merkür": swe.MERCURY,
    "Venüs": swe.VENUS,
    "Mars": swe.MARS,
    "Jüpiter": swe.JUPITER,
    "Satürn": swe.SATURN
}

ACILAR = [
    {"ad": "Kavuşum (0°)", "hedef": 0, "orb": 6},
    {"ad": "Sekstil (60°)", "hedef": 60, "orb": 4},
    {"ad": "Kare (90°)", "hedef": 90, "orb": 5},
    {"ad": "Üçgen (120°)", "hedef": 120, "orb": 5},
    {"ad": "Karşıt (180°)", "hedef": 180, "orb": 6},
]

def dogum_haritasi_hesapla(yil, ay, gun, saat=None, dakika=None):
    saat_biliniyor = True
    if saat is None or dakika is None:
        saat = 12
        dakika = 0
        saat_biliniyor = False

    ondalik_saat = saat + (dakika / 60.0)
    jul_gun = swe.julday(yil, ay, gun, ondalik_saat)

    harita = {"_meta": {"saat_biliniyor": saat_biliniyor}}
    for gezegen_adi, gezegen_kodu in GEZEGENLER.items():
        bilgi, _ = swe.calc_ut(jul_gun, gezegen_kodu)
        boylam = bilgi[0]

        burc_index = int(boylam // 30)
        burctaki_derece = round(boylam % 30, 2)

        harita[gezegen_adi] = {
            "burc": BURCLAR[burc_index],
            "derece": burctaki_derece,
            "mutlak_derece": round(boylam, 2)
        }
    return harita

def sinastri_acilarini_bul(harita1, harita2):
    bulunan_acilar = []
    p1_gezegenler = {k: v for k, v in harita1.items() if k != "_meta"}
    p2_gezegenler = {k: v for k, v in harita2.items() if k != "_meta"}

    for p1_gezegen, p1_bilgi in p1_gezegenler.items():
        for p2_gezegen, p2_bilgi in p2_gezegenler.items():
            fark = abs(p1_bilgi["mutlak_derece"] - p2_bilgi["mutlak_derece"])
            if fark > 180:
                fark = 360 - fark

            for aci in ACILAR:
                hata_payi = abs(fark - aci["hedef"])
                if hata_payi <= aci["orb"]:
                    bulunan_acilar.append({
                        "partner1": f"P1 {p1_gezegen} ({p1_bilgi['burc']})",
                        "partner2": f"P2 {p2_gezegen} ({p2_bilgi['burc']})",
                        "aci": aci["ad"],
                        "orb": round(hata_payi, 2)
                    })
    return bulunan_acilar