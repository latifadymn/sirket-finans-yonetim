import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Uygulama Başlığı
st.set_page_config(page_title="Holding Pro", layout="wide")
st.title("💼 Godson - Fynix - Prifa: Stratejik Finans Paneli")

# --- ÖRNEK VERİ (Başlangıçta ekranın boş kalmaması için) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame([
        {'Birim': 'Godson Teknoloji', 'Tür': 'Gelir', 'Kategori': 'Yazılım Satış', 'Miktar': 50000, 'Tarih': '2026-01-01'},
        {'Birim': 'Prifa Kahvecilik', 'Tür': 'Gider', 'Kategori': 'Hammadde', 'Miktar': 15000, 'Tarih': '2026-01-02'}
    ])

# --- DASHBOARD SAYFASI ---
def show_dashboard():
    df = st.session_state.data
    
    # Şirket Bazlı Sekmeler
    tabs = st.tabs(["Genel Bakış", "Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Yatırımlar & Kişisel"])

    with tabs[0]: # Genel Bakış
        st.subheader("Konsolide Durum")
        col1, col2, col3 = st.columns(3)
        total_gelir = df[df['Tür']=='Gelir']['Miktar'].sum()
        total_gider = df[df['Tür']=='Gider']['Miktar'].sum()
        col1.metric("Toplam Ciro", f"{total_gelir:,.0f} TL")
        col2.metric("Toplam Masraf", f"{total_gider:,.0f} TL")
        col3.metric("Net Kâr", f"{total_gelir - total_gider:,.0f} TL")
        
        fig_genel = px.sunburst(df, path=['Birim', 'Tür', 'Kategori'], values='Miktar', title="Holding Harcama/Gelir Dağılım Şeması")
        st.plotly_chart(fig_genel, use_container_width=True)

    # Şirketlerin Özel Sayfaları (Döngü ile oluşturabiliriz)
    for i, sirket in enumerate(["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"]):
        with tabs[i+1]:
            s_df = df[df['Birim'] == sirket]
            if not s_df.empty:
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.write(f"**{sirket} Finansal Özeti**")
                    s_gelir = s_df[s_df['Tür']=='Gelir']['Miktar'].sum()
                    s_gider = s_df[s_df['Tür']=='Gider']['Miktar'].sum()
                    st.info(f"Kâr/Zarar: {s_gelir - s_gider:,.0f} TL")
                with c2:
                    fig_sirket = px.pie(s_df, values='Miktar', names='Kategori', title=f"{sirket} Gider Dağılımı", hole=0.4)
                    st.plotly_chart(fig_sirket, use_container_width=True)
            else:
                st.write("Henüz veri girilmemiş.")

# --- YAN MENÜ ---
menu = st.sidebar.radio("Yönetim", ["📊 Dashboard", "➕ Veri Girişi", "⏳ Zaman Dağıtım Paneli"])

if menu == "📊 Dashboard":
    show_dashboard()

elif menu == "➕ Veri Girişi":
    with st.form("giriş"):
        birim = st.selectbox("Birim", ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Kişisel/Yatırım"])
        tur = st.radio("Tür", ["Gelir", "Gider"])
        kat = st.selectbox("Kategori", ["Maaş", "Yazılım/Altyapı", "Pazarlama", "Stok", "Kira", "Yatırım Getirisi", "Diğer"])
        tutar = st.number_input("Tutar", min_value=0.0)
        if st.form_submit_button("Kaydet"):
            new_data = pd.DataFrame([{'Birim': birim, 'Tür': tur, 'Kategori': kat, 'Miktar': tutar, 'Tarih': str(datetime.now())}])
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            st.success("Kayıt eklendi!")

elif menu == "⏳ Zaman Dağıtım Paneli":
    st.subheader("Zaman ve Dolaylı Gider Yönetimi")
    st.write("Kendi masraflarını şirketlere zaman oranına göre yansıt.")
    masraf = st.number_input("Dağıtılacak Şahsi Masraf (Örn: Maaşın, Aracın vb.)", min_value=0.0)
    
    g_o = st.slider("Godson Zaman %", 0, 100, 33)
    f_o = st.slider("Fynix Zaman %", 0, 100, 33)
    p_o = st.slider("Prifa Zaman %", 0, 100, 34)
    
    if st.button("Masrafı Şirketlere Bölüştür"):
        for s, o in zip(["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"], [g_o, f_o, p_o]):
            yansiyan = masraf * (o/100)
            new_row = pd.DataFrame([{'Birim': s, 'Tür': 'Gider', 'Kategori': 'Zaman Maliyeti', 'Miktar': yansiyan, 'Tarih': str(datetime.now())}])
            st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
        st.success("İşlem Başarılı!")
