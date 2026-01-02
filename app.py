import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Sayfa Ayarları
st.set_page_config(page_title="Holding Finans Paneli", layout="wide")

# --- VERİ İLKELENDİRME ---
if 'data' not in st.session_state:
    # Başlangıçta boş bir DataFrame oluşturuyoruz
    st.session_state.data = pd.DataFrame(columns=[
        'Birim', 'Tür', 'Kategori', 'Miktar', 'Tarih', 'Durum', 'Not'
    ])

# --- YAN MENÜ ---
st.sidebar.title("Holding Yönetimi")
menu = st.sidebar.radio("Sayfa Seçin", [
    "📊 Genel Perspektif", 
    "🏢 Şirket Değerlemeleri",
    "➕ İşlem Ekle & Planla", 
    "🎯 Yatırım Rehberi"
])

# Verileri Tarih Formatına Çevir (Hata önleyici)
if not st.session_state.data.empty:
    st.session_state.data['Tarih'] = pd.to_datetime(st.session_state.data['Tarih']).dt.date

# --- SAYFA 1: GENEL PERSPEKTİF (6 AY) ---
if menu == "📊 Genel Perspektif":
    st.header("📈 6 Aylık Finansal Projeksiyon")
    df = st.session_state.data
    
    if df.empty:
        st.info("Henüz veri yok. Lütfen işlem ekleyin.")
    else:
        # Gelecek 6 ayın sınırlarını belirle
        bugun = date.today()
        alt_ay_sonra = bugun + relativedelta(months=6)
        
        # Grafik Verisi Hazırlama
        df_viz = df.copy()
        df_viz['Ay'] = pd.to_datetime(df_viz['Tarih']).dt.strftime('%Y-%m')
        
        # Aylık Özet Tablo
        aylik_ozet = df_viz.groupby(['Ay', 'Tür'])['Miktar'].sum().reset_index()
        
        fig = px.line(aylik_ozet, x='Ay', y='Miktar', color='Tür', markers=True,
                     title="Aylık Gelir ve Gider Trendi (Gelecek Odaklı)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Ödeme Takip Listesi
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔴 Bekleyen Ödemeler")
            st.dataframe(df[(df['Tür']=='Gider') & (df['Durum']=='Beklemede')], use_container_width=True)
        with col2:
            st.subheader("🟢 Bekleyen Tahsilatlar")
            st.dataframe(df[(df['Tür']=='Gelir') & (df['Durum']=='Beklemede')], use_container_width=True)

# --- SAYFA 2: ŞİRKET DEĞERLEMELERİ ---
elif menu == "🏢 Şirket Değerlemeleri":
    st.header("💎 Şirket Bazlı Değerleme ve Tarihsel Durum")
    df = st.session_state.data
    sirketler = ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"]
    
    for sirket in sirketler:
        with st.expander(f"{sirket} Analizi", expanded=True):
            s_df = df[df['Birim'] == sirket]
            gelir = s_df[s_df['Tür']=='Gelir']['Miktar'].sum()
            gider = s_df[s_df['Tür']=='Gider']['Miktar'].sum()
            kar = gelir - gider
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Toplam Gelir", f"{gelir:,.0f} TL")
            c2.metric("Toplam Gider", f"{gider:,.0f} TL")
            c3.metric("Net Kâr", f"{kar:,.0f} TL")
            c4.metric("Değerleme (x5)", f"{max(0, kar*5):,.0f} TL", delta="Tahmini")
            
            # Şirkete Özel Gelir-Gider Şeması
            if not s_df.empty:
                fig_pie = px.pie(s_df, values='Miktar', names='Tür', hole=0.5, 
                                 color_discrete_map={'Gelir':'#2ecc71', 'Gider':'#e74c3c'})
                st.plotly_chart(fig_pie, use_container_width=True)

# --- SAYFA 3: İŞLEM EKLE & PLANLA ---
elif menu == "➕ İşlem Ekle & Planla":
    st.header("Yeni İşlem Girişi")
    with st.form("islem_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            birim = st.selectbox("Birim", ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Kişisel/Yatırım"])
            tur = st.radio("İşlem Türü", ["Gelir", "Gider"], horizontal=True)
            miktar = st.number_input("Tutar (TL)", min_value=0.0, format="%.2f")
            tarih = st.date_input("Başlangıç Tarihi", value=date.today())
        with col2:
            kat = st.text_input("Kategori (Kira, Maaş, Satış vb.)")
            durum = st.selectbox("Durum", ["Gerçekleşti", "Beklemede"])
            tekrar = st.selectbox("Periyot", ["Tek Seferlik", "6 Ay Tekrarla", "12 Ay Tekrarla"])
            not_al = st.text_input("Not")
            
        if st.form_submit_button("Kaydet"):
            dongu = 1
            if "6 Ay" in tekrar: dongu = 6
            if "12 Ay" in tekrar: dongu = 12
            
            yeni_veriler = []
            for i in range(dongu):
                islem_tarihi = tarih + relativedelta(months=i)
                yeni_veriler.append({
                    'Birim': birim, 'Tür': tur, 'Kategori': kat, 
                    'Miktar': miktar, 'Tarih': islem_tarihi, 
                    'Durum': durum, 'Not': not_al
                })
            
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame(yeni_veriler)], ignore_index=True)
            st.success(f"{dongu} işlem başarıyla eklendi!")

# --- SAYFA 4: YATIRIM REHBERİ ---
elif menu == "🎯 Yatırım Rehberi":
    st.header("Kişisel Yatırım ve Sermaye Planlama")
    gelir_giris = st.number_input("Aylık Kişisel Gelirinizi Girin (TL)", min_value=0.0)
    
    if gelir_giris > 0:
        y_butcesi = gelir_giris * 0.10
        st.metric("Aylık Yatırım Bütçeniz (%10)", f"{y_butcesi:,.0f} TL")
        
        st.write("### Stratejik Yatırım Önerisi")
        col1, col2, col3 = st.columns(3)
        col1.info(f"**Godson (%40)**\n\n {y_butcesi*0.4:,.0f} TL\n(Teknoloji Geliştirme)")
        col2.info(f"**Fynix (%40)**\n\n {y_butcesi*0.4:,.0f} TL\n(Operasyonel Büyüme)")
        col3.info(f"**Prifa (%20)**\n\n {y_butcesi*0.2:,.0f} TL\n(Stok ve Fiziksel Alan)")
