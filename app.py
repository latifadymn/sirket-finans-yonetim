import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Holding Finans Pro", layout="wide")

# --- VERİ YÖNETİMİ ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['Birim', 'Tür', 'Kategori', 'Miktar', 'Tarih'])

# --- YAN MENÜ: VERİ TEMİZLEME ---
if st.sidebar.button("⚠️ Tüm Verileri Sıfırla"):
    st.session_state.data = pd.DataFrame(columns=['Birim', 'Tür', 'Kategori', 'Miktar', 'Tarih'])
    st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.radio("Yönetim Paneli", ["📊 Dashboard", "➕ Veri Girişi", "⏳ Zaman Dağıtımı"])

# --- SAYFA 1: DASHBOARD ---
if menu == "📊 Dashboard":
    st.title("🚀 Holding Stratejik Görünüm")
    df = st.session_state.data

    if df.empty:
        st.warning("Henüz veri girişi yapılmadı. Lütfen 'Veri Girişi' sekmesini kullanın.")
    else:
        # Şirket Sekmeleri
        tabs = st.tabs(["Holding Genel", "Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"])

        # 1. HOLDİNG GENEL
        with tabs[0]:
            c1, c2, c3 = st.columns(3)
            gelir = df[df['Tür']=='Gelir']['Miktar'].sum()
            gider = df[df['Tür']=='Gider']['Miktar'].sum()
            c1.metric("Toplam Gelir", f"{gelir:,.0f} TL")
            c2.metric("Toplam Gider", f"{gider:,.0f} TL")
            c3.metric("Net Nakit Akışı", f"{gelir-gider:,.0f} TL")
            
            fig_bar = px.bar(df, x='Birim', y='Miktar', color='Tür', barmode='group', title="Şirketler Arası Karşılaştırma")
            st.plotly_chart(fig_bar, use_container_width=True)

        # 2. ŞİRKET ÖZEL SAYFALARI
        sirketler = ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"]
        for i, sirket in enumerate(sirketler):
            with tabs[i+1]:
                s_df = df[df['Birim'] == sirket]
                if s_df.empty:
                    st.info(f"{sirket} için henüz veri yok.")
                    continue
                
                # İKİ AYRI ŞEMA: GELİR VE GİDER
                col_geli, col_gide = st.columns(2)
                
                with col_geli:
                    gelir_df = s_df[s_df['Tür'] == 'Gelir']
                    if not gelir_df.empty:
                        fig_gelir = px.pie(gelir_df, values='Miktar', names='Kategori', 
                                          title=f"{sirket} Gelir Dağılımı", hole=0.4,
                                          color_discrete_sequence=px.colors.sequential.Greens)
                        st.plotly_chart(fig_gelir, use_container_width=True)
                    else:
                        st.write("Gelir verisi yok.")

                with col_gide:
                    gider_df = s_df[s_df['Tür'] == 'Gider']
                    if not gider_df.empty:
                        fig_gider = px.pie(gider_df, values='Miktar', names='Kategori', 
                                          title=f"{sirket} Gider Dağılımı", hole=0.4,
                                          color_discrete_sequence=px.colors.sequential.OrRd)
                        st.plotly_chart(fig_gider, use_container_width=True)
                    else:
                        st.write("Gider verisi yok.")

# --- SAYFA 2: VERİ GİRİŞİ ---
elif menu == "➕ Veri Girişi":
    st.subheader("Finansal İşlem Kaydı")
    with st.form("islem_formu", clear_on_submit=True):
        b = st.selectbox("Şirket/Birim", ["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik", "Kişisel/Yatırım"])
        t = st.radio("İşlem Türü", ["Gelir", "Gider"], horizontal=True)
        m = st.number_input("Miktar (TL)", min_value=0.0)
        k = st.text_input("Kategori (Örn: Maaş, Satış, Kira, Kripto)")
        tarih = st.date_input("Tarih")
        
        if st.form_submit_button("Sisteme İşle"):
            yeni_satir = pd.DataFrame([{'Birim': b, 'Tür': t, 'Kategori': k, 'Miktar': m, 'Tarih': tarih}])
            st.session_state.data = pd.concat([st.session_state.data, yeni_satir], ignore_index=True)
            st.success("Kayıt başarıyla eklendi!")

# --- SAYFA 3: ZAMAN DAĞITIMI ---
elif menu == "⏳ Zaman Dağıtımı":
    st.subheader("Zaman Bazlı Gider Yansıtma")
    st.write("Kendi eforunu ve şahsi masraflarını şirketlere paylaştır.")
    toplam = st.number_input("Dağıtılacak Toplam Tutar", min_value=0.0)
    
    c1, c2, c3 = st.columns(3)
    g_o = c1.number_input("Godson %", 0, 100, 33)
    f_o = c2.number_input("Fynix %", 0, 100, 33)
    p_o = c3.number_input("Prifa %", 0, 100, 34)
    
    if st.button("Dağıtımı Onayla"):
        for s, o in zip(["Godson Teknoloji", "Fynix Teknoloji", "Prifa Kahvecilik"], [g_o, f_o, p_o]):
            pay = toplam * (o/100)
            yeni_satir = pd.DataFrame([{'Birim': s, 'Tür': 'Gider', 'Kategori': 'Zaman Maliyeti', 'Miktar': pay, 'Tarih': datetime.now()}])
            st.session_state.data = pd.concat([st.session_state.data, yeni_satir], ignore_index=True)
        st.success("Masraflar şirket bilançolarına aktarıldı!")
