import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Uygulama Başlığı ve Ayarlar
st.set_page_config(page_title="Holding Finans Paneli", layout="wide")
st.title("🏦 Şirketler & Yatırım Yönetim Merkezi")

# --- VERİ YAPISI (Basitlik için Session State kullanıyoruz) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Birim', 'Tür', 'Kategori', 'Miktar', 'Tarih', 'Not'])

# --- YAN MENÜ ---
menu = ["📊 Dashboard", "➕ İşlem Ekle", "⏳ Zaman & Masraf Dağıtımı", "📈 Al-Sat/Yatırım"]
choice = st.sidebar.selectbox("Yönetim Menüsü", menu)

# --- SAYFA 1: İŞLEM EKLE ---
if choice == "➕ İşlem Ekle":
    st.subheader("Yeni Finansal Kayıt")
    with st.form("islem_formu"):
        col1, col2 = st.columns(2)
        with col1:
            birim = st.selectbox("İlgili Birim", ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Kişisel/Yatırım"])
            tur = st.radio("İşlem Türü", ["Gelir", "Gider"])
            miktar = st.number_input("Tutar (TL)", min_value=0.0)
        with col2:
            tarih = st.date_input("İşlem Tarihi", datetime.now())
            kat = st.selectbox("Kategori", ["Maaş/Hakediş", "Yazılım/SaaS", "Stok/Hammadde", "Kira/Ofis", "Pazarlama", "Al-Sat Kar", "Diğer"])
            notlar = st.text_input("Kısa Not")
        
        submit = st.form_submit_button("Kaydı Tamamla")
        if submit:
            new_row = {'Birim': birim, 'Tür': tur, 'Kategori': kat, 'Miktar': miktar, 'Tarih': tarih, 'Not': notlar}
            st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Kayıt başarıyla eklendi!")

# --- SAYFA 2: ZAMAN & MASRAF DAĞITIMI ---
elif choice == "⏳ Zaman & Masraf Dağıtımı":
    st.subheader("Zaman Bazlı Dolaylı Gider Yansıtma")
    st.info("Kişisel masraflarını, şirketlere ayırdığın vakte göre paylaştır.")
    
    toplam_kisisel = st.number_input("Bu Ayki Toplam Kişisel Masrafın (TL)", min_value=0.0)
    
    st.write("Vakit Ayırma Oranları (%)")
    c1, c2, c3 = st.columns(3)
    g_p = c1.slider("Godson %", 0, 100, 33)
    f_p = c2.slider("Fynix %", 0, 100, 33)
    p_p = c3.slider("Prifa %", 0, 100, 34)
    
    if st.button("Masrafları Şirketlere Dağıt"):
        if g_p + f_p + p_p == 100:
            dist = {
                "Godson Teknoloji": toplam_kisisel * (g_p/100),
                "Fynix Teknoloji": toplam_kisisel * (f_p/100),
                "Prifa Kahvecilik": toplam_kisisel * (p_p/100)
            }
            for sirket, tutar in dist.items():
                row = {'Birim': sirket, 'Tür': 'Gider', 'Kategori': 'Zaman/Maliyet Yansıması', 'Miktar': tutar, 'Tarih': datetime.now(), 'Not': 'Otomatik yansıtma'}
                st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([row])], ignore_index=True)
            st.success("Tüm masraflar şirket bilançolarına işlendi!")
        else:
            st.error("Toplam oran %100 olmalıdır!")

# --- SAYFA 3: DASHBOARD ---
elif choice == "📊 Dashboard":
    st.subheader("Genel Finansal Durum")
    if not st.session_state.data.empty:
        df = st.session_state.data
        
        # Filtreler
        sirket_filtre = st.multiselect("Şirket Seçin", df['Birim'].unique(), default=df['Birim'].unique())
        mask = df['Birim'].isin(sirket_filtre)
        filtered_df = df[mask]
        
        # Özet Kartlar
        gelir = filtered_df[filtered_df['Tür'] == 'Gelir']['Miktar'].sum()
        gider = filtered_df[filtered_df['Tür'] == 'Gider']['Miktar'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Gelir", f"{gelir:,.2f} TL")
        c2.metric("Toplam Gider", f"{gider:,.2f} TL")
        c3.metric("Net Durum", f"{(gelir-gider):,.2f} TL", delta=float(gelir-gider))
        
        # Grafikler
        fig = px.bar(filtered_df, x='Birim', y='Miktar', color='Tür', barmode='group', title="Şirket Bazlı Gelir/Gider")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(filtered_df)
    else:
        st.warning("Henüz veri girilmemiş.")
