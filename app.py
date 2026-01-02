import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Holding Strateji Merkezi", layout="wide")

# --- VERİ YAPISI GÜNCELLEME ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        'Birim', 'Tür', 'Kategori', 'Miktar', 'Tarih', 'Durum', 'Tekrar'
    ])

# --- FONKSİYONLAR ---
def adds_months(sourcedate, months):
    import calendar
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day).date()

# --- YAN MENÜ ---
menu = st.sidebar.radio("Stratejik Yönetim", [
    "📊 Genel Perspektif", 
    "🏢 Şirket Değerlemeleri",
    "➕ İşlem ve Planlama", 
    "⏳ Zaman & Kişisel Yatırım"
])

# --- SAYFA 1: GENEL PERSPEKTİF (6 AYLIK) ---
if menu == "📊 Genel Perspektif":
    st.title("📈 6 Aylık Finansal Perspektif")
    df = st.session_state.data
    
    if not df.empty:
        df['Tarih'] = pd.to_datetime(df['Tarih']).dt.date
        bugun = datetime.now().date()
        alti_ay_sonra = adds_months(bugun, 6)
        
        # Gelecek Perspektifi Filtresi
        mask = (df['Tarih'] >= bugun.replace(day=1)) & (df['Tarih'] <= alti_ay_sonra)
        p_df = df[mask].copy()
        p_df['Ay'] = pd.to_datetime(p_df['Tarih']).dt.strftime('%Y-%m')
        
        # Nakit Akış Grafiği
        cash_flow = p_df.groupby(['Ay', 'Tür'])['Miktar'].sum().reset_index()
        fig_line = px.line(cash_flow, x='Ay', y='Miktar', color='Tür', 
                          title="Önümüzdeki 6 Ayın Tahmini Nakit Akışı", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Ödeme Durumu Takibi
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Bekleyen Tahsilatlar (Gelir)")
            st.dataframe(df[(df['Tür']=='Gelir') & (df['Durum']=='Beklemede')])
        with col2:
            st.subheader("Ödenecek Masraflar (Gider)")
            st.dataframe(df[(df['Tür']=='Gider') & (df['Durum']=='Beklemede')])

# --- SAYFA 2: ŞİRKET DEĞERLEMELERİ ---
elif menu == "🏢 Şirket Değerlemeleri":
    st.title("💎 Şirket Bazlı Kümülatif Değerleme")
    df = st.session_state.data
    sirketler = ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"]
    
    for sirket in sirketler:
        s_df = df[df['Birim'] == sirket]
        with st.expander(f"{sirket} - Detaylı Analiz", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            top_gelir = s_df[s_df['Tür']=='Gelir']['Miktar'].sum()
            top_gider = s_df[s_df['Tür']=='Gider']['Miktar'].sum()
            net_kar = top_gelir - top_gider
            
            c1.metric("Toplam Ciro", f"{top_gelir:,.0f} TL")
            c2.metric("Toplam Masraf", f"{top_gider:,.0f} TL")
            c3.metric("Net Kâr/Zarar", f"{net_kar:,.0f} TL")
            c4.metric("Tahmini Değerleme (x5 Kar)", f"{max(0, net_kar*5):,.0f} TL")

# --- SAYFA 3: İŞLEM VE PLANLAMA (FONKSİYONEL GİRİŞ) ---
elif menu == "➕ İşlem ve Planlama":
    st.subheader("İşlem Kaydı ve Otomatik Planlama")
    with st.form("gelismis_giris"):
        col1, col2 = st.columns(2)
        with col1:
            birim = st.selectbox("Birim", ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Kişisel/Yatırım"])
            tur = st.radio("Tür", ["Gelir", "Gider"], horizontal=True)
            miktar = st.number_input("Miktar", min_value=0.0)
            tarih = st.date_input("Başlangıç Tarihi")
        with col2:
            durum = st.selectbox("Durum", ["Gerçekleşti", "Beklemede"])
            tekrar = st.selectbox("Tekrarlansın mı?", ["Hayır", "6 Ay Boyunca Tekrarla", "12 Ay Boyunca Tekrarla"])
            kat = st.text_input("Kategori")
            
        if st.form_submit_button("Sisteme Kaydet"):
            dongu = 1
            if "6 Ay" in tekrar: dongu = 6
            if "12 Ay" in tekrar: dongu = 12
            
            new_rows = []
            for i in range(dongu):
                new_date = adds_months(tarih, i)
                new_rows.append({'Birim': birim, 'Tür': tur, 'Kategori': kat, 'Miktar': miktar, 'Tarih': new_date, 'Durum': durum, 'Tekrar': tekrar})
            
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame(new_rows)], ignore_index=True)
            st.success(f"{dongu} adet işlem başarıyla planlandı!")

# --- SAYFA 4: ZAMAN & KİŞİSEL YATIRIM ---
elif menu == "⏳ Zaman & Kişisel Yatırım":
    st.title("🎯 Yatırım ve Efor Yönetimi")
    df = st.session_state.data
    
    kisisel_gelir = st.number_input("Aylık Kişisel Gelirin (TL)", min_value=0.0)
    y_orani = 0.10
    y_butcesi = kisisel_gelir * y_orani
    
    st.metric("Aylık Yatırım Bütçen (%10)", f"{y_butcesi:,.0f} TL")
    st.info(f"Bu bütçeyi Godson (%40), Fynix (%40) ve Prifa (%20) arasında bölüştürmen sermaye büyümesi için önerilir.")
    
    # Zaman Dağıtımı (Önceki mantıkla aynı)
    st.write("---")
    st.subheader("Zaman Bazlı Gider Yansıtma")
    # ... (Zaman slider'ları ve dağıtım butonu buraya eklenebilir)
