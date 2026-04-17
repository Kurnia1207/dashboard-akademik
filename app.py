import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Dashboard Akademik", layout="wide")

# -- PANEL ADMIN DI KIRI --
st.sidebar.header("⚙️ Panel Update Data")
st.sidebar.warning("Pastikan perangkat terhubung internet. Gunakan tombol di bawah ini untuk memperbarui data.")

# Tombol input dokumen dibuat sangat jelas
uploaded_file = st.sidebar.file_uploader("📂 Upload Dokumen CSV di sini", type=['csv'])

# -- TAMPILAN PIMPINAN --
st.title("📊 Dashboard Laporan Info Akademik")

if uploaded_file is not None:
    # Membaca data yang baru saja diunggah admin
    df = pd.read_csv(uploaded_file, skiprows=2)
    df.columns = ['PRODI', '2017_2', '2018_2', '2019_2', '2020_2', '2021_2', '2022_2', '2023_2', '2024_2', 'JUMLAH']
    df = df.dropna(subset=['PRODI'])
    
    df_melt = df.melt(id_vars=['PRODI'], 
                      value_vars=['2017_2', '2018_2', '2019_2', '2020_2', '2021_2', '2022_2', '2023_2', '2024_2'], 
                      var_name='Periode', value_name='Jumlah Lulusan')
    
    # Menampilkan Grafik
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tren Kelulusan per Periode")
        fig_bar = px.bar(df_melt, x='Periode', y='Jumlah Lulusan', color='PRODI', barmode='group')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("Proporsi Total Lulusan")
        fig_pie = px.pie(df, names='PRODI', values='JUMLAH', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.sidebar.success("✅ Data berhasil diupdate ke sistem!")
else:
    st.info("👈 Silakan arahkan pandangan ke panel sebelah kiri. Klik tombol 'Browse files' untuk memasukkan dokumen data agar grafik muncul.")