import streamlit as st
import datetime
from datetime import date
import csv
import os
from google import genai
from astro_motoru import dogum_haritasi_hesapla, sinastri_acilarini_bul

# Sayfa Yapılandırması (İlk orijinal sade yapı)
st.set_page_config(page_title="Sinastri Analizi", page_icon="✨", layout="wide")

st.title("✨ Astroloji Sinastri ve Uyum Analizi")
st.write("Partnerlerin doğum bilgilerini girerek harita yerleşimlerini ve yapay zeka analizini görüntüleyin.")

# API İstemcisi
# API İstemcisi
api_key = st.secrets.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)

# Arka planda gizlice tutulan kayıt dosyası
CSV_DOSYASI = "sorgu_gecmisi.csv"

def sorguyu_kaydet(p1_isim, p1_tarih, p1_saat, p2_isim, p2_tarih, p2_saat):
    dosya_yok = not os.path.exists(CSV_DOSYASI)
    with open(CSV_DOSYASI, mode="a", newline="", encoding="utf-8") as f:
        yazici = csv.writer(f)
        if dosya_yok:
            yazici.writerow(["Sorgu Zamanı", "Partner 1", "P1 Tarih", "P1 Saat", "Partner 2", "P2 Tarih", "P2 Saat"])
        
        simdi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yazici.writerow([
            simdi,
            p1_isim if p1_isim else "İsimsiz 1",
            p1_tarih,
            p1_saat if p1_saat else "Bilinmiyor (12:00)",
            p2_isim if p2_isim else "İsimsiz 2",
            p2_tarih,
            p2_saat if p2_saat else "Bilinmiyor (12:00)"
        ])

col1, col2 = st.columns(2)

with col1:
    st.subheader("Partner 1 Bilgileri")
    p1_isim = st.text_input("İsim / Lakap (P1)", placeholder="Örn: Dilek", key="isim1")
    
    d1 = st.date_input(
    "Doğum Tarihi (P1)",
    value=date(2000, 5, 14),
    min_value=date(1920, 1, 1),
    max_value=date.today()
)



    biliniyor1 = st.checkbox("Doğum saatini biliyorum", value=True, key="c1")
    t1 = st.time_input("Doğum Saati (P1)", datetime.time(15, 30), key="t1") if biliniyor1 else None

with col2:
    st.subheader("Partner 2 Bilgileri")
    p2_isim = st.text_input("İsim / Lakap (P2)", placeholder="Örn: Orhan", key="isim2")
    
    d2 = st.date_input(
    "Doğum Tarihi (P2)",
    value=date(2001, 10, 22),
    min_value=date(1920, 1, 1),
    max_value=date.today()
    )
    biliniyor2 = st.checkbox("Doğum saatini biliyorum", value=False, key="c2")
    t2 = st.time_input("Doğum Saati (P2)", datetime.time(12, 0), key="t2") if biliniyor2 else None

if st.button("Uyum Analizini Başlat 🔮", type="primary"):
    p1_saat = t1.hour if biliniyor1 else None
    p1_dakika = t1.minute if biliniyor1 else None
    
    p2_saat = t2.hour if biliniyor2 else None
    p2_dakika = t2.minute if biliniyor2 else None

    # Arka plan kaydı (Kullanıcı arayüzünde görünmez)
    sorguyu_kaydet(
        p1_isim, str(d1), f"{p1_saat:02d}:{p1_dakika:02d}" if biliniyor1 else None,
        p2_isim, str(d2), f"{p2_saat:02d}:{p2_dakika:02d}" if biliniyor2 else None
    )

    p1_bilgi = (d1.year, d1.month, d1.day, p1_saat, p1_dakika)
    p2_bilgi = (d2.year, d2.month, d2.day, p2_saat, p2_dakika)

    with st.spinner("Gezegen konumları hesaplanıyor ve Gemini analizi hazırlanıyor..."):
        h1 = dogum_haritasi_hesapla(*p1_bilgi)
        h2 = dogum_haritasi_hesapla(*p2_bilgi)
        acilar = sinastri_acilarini_bul(h1, h2)

        uyarilar = []
        if not h1["_meta"]["saat_biliniyor"]:
            uyarilar.append(f"- {p1_isim or 'Partner 1'} doğum saati bilinmiyor (12:00 alındı).")
        if not h2["_meta"]["saat_biliniyor"]:
            uyarilar.append(f"- {p2_isim or 'Partner 2'} doğum saati bilinmiyor (12:00 alındı).")

        prompt = f"""
        Aşağıdaki gezegen yerleşimlerini ve sinastri açılarını kısaca özetle:
        PARTNER 1 ({p1_isim or 'Partner 1'}): {h1}
        PARTNER 2 ({p2_isim or 'Partner 2'}): {h2}
        AÇILAR: {acilar}
        DURUMLAR: {chr(10).join(uyarilar) if uyarilar else 'Saatler tam.'}

        Raporu 3 başlıkta yaz:
        1. {p1_isim or 'Partner 1'} Karakter Özeti
        2. {p2_isim or 'Partner 2'} Karakter Özeti
        3. İlişki Uyumu ve Dikkat Edilecekler
        """

        cevap = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

    st.success("Analiz tamamlandı!")
    
    tab1, tab2 = st.tabs(["📝 Yapay Zeka Yorumu", "🪐 Gezegen Yerleşimleri"])
    with tab1:
        st.markdown(cevap.text)
    with tab2:
        st.json({p1_isim or "Partner 1": h1, p2_isim or "Partner 2": h2, "Sinastri Açıları": acilar})

# Created By İmzası
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Created by <b>Yaren Nurhak Yeşil</b> ✨</p>", 
    unsafe_allow_html=True
)
# --- GİZLİ YÖNETİCİ GEÇMİŞ İNDİRME ALANI ---
import os

if st.query_params.get("admin") == "1":
    st.divider()
    st.subheader("🔒 Yönetici Paneli")
    csv_adi = "analiz_kayitlari.csv"
    if os.path.exists(csv_adi):
        with open(csv_adi, "rb") as f:
            st.download_button(
                label="📥 Analiz Geçmişini İndir (CSV)",
                data=f,
                file_name="analiz_kayitlari.csv",
                mime="text/csv"
            )
    else:
        st.info("Kayıt dosyası henüz oluşmadı veya henüz analiz yapılmadı.")