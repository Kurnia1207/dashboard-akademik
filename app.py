import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman Utama
st.set_page_config(page_title="Dashboard Akademik", layout="wide")

# -- PANEL ADMIN DI KIRI --
st.sidebar.header("⚙️ Panel Update Data")
st.sidebar.warning("Gunakan tombol di bawah ini untuk memperbarui data.")

# Tombol input dokumen khusus untuk file yang baru
uploaded_file = st.sidebar.file_uploader("📂 Upload Dokumen CSV Vokasi di sini", type=['csv'])

# -- TAMPILAN PIMPINAN --
st.title("📊 Dashboard Laporan Perkembangan Mahasiswa Aktif & Lulusan")
st.markdown("Menampilkan dinamika Mahasiswa Baru (MABA), Lulusan, dan Total Mahasiswa Aktif berdasarkan rekapitulasi data Fakultas Vokasi.")

if uploaded_file is not None:
    try:
        # Membaca data dengan pemisah titik koma (;) dan melewati 4 baris pertama (header)
        df = pd.read_csv(uploaded_file, sep=';', skiprows=4)
        
        # Merapikan nama kolom
        cols = list(df.columns)
        cols[0] = 'TAHUN MASUK'
        
        # Kolom ke-35 adalah posisi kolom "TOTAL JUMLAH LULUSAN" berdasarkan file CSV Anda
        if len(cols) > 35:
            cols[35] = 'TOTAL LULUSAN'
        df.columns = cols
        
        # Membersihkan data (hanya mengambil baris yang 'TAHUN MASUK'-nya berupa angka tahun)
        df = df.dropna(axis=1, how='all')
        df = df[df['TAHUN MASUK'].astype(str).str.isnumeric()].copy()
        
        # Memisahkan kolom-kolom periode (contoh: 2014_1, 2014_2, dst)
        period_cols = [c for c in df.columns if '_' in c]
        for col in period_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # --- PENGOLAHAN DATA METRIK ---
        # 1. Mendapatkan Jumlah Mahasiswa Baru (MABA) per Tahun Masuk 
        # (Diambil dari angka pertama saat mereka masuk)
        df['MABA'] = df[period_cols].bfill(axis=1).iloc[:, 0]
        
        # 2. Menghitung Total Mahasiswa Aktif dari gabungan semua angkatan per periode
        active_per_period = df[period_cols].sum().reset_index()
        active_per_period.columns = ['Periode', 'Total Mahasiswa Aktif']
        
        # Menyiapkan data yang sudah rapi
        df_summary = df[['TAHUN MASUK', 'MABA', 'TOTAL LULUSAN']].copy()
        df_summary['TAHUN MASUK'] = df_summary['TAHUN MASUK'].astype(str)
        
        # --- VISUALISASI ---
        # Baris Pertama: Grafik MABA & Grafik Lulusan
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tren Mahasiswa Baru per Angkatan")
            fig_maba = px.bar(df_summary, x='TAHUN MASUK', y='MABA', 
                              text='MABA', color_discrete_sequence=['#1E88E5'])
            fig_maba.update_traces(textposition='outside')
            st.plotly_chart(fig_maba, use_container_width=True)

        with col2:
            st.subheader("Total Kelulusan per Angkatan")
            # Menghapus angkatan yang belum memiliki lulusan agar grafik bersih
            df_lulusan = df_summary.dropna(subset=['TOTAL LULUSAN'])
            fig_lulus = px.bar(df_lulusan, x='TAHUN MASUK', y='TOTAL LULUSAN', 
                               text='TOTAL LULUSAN', color_discrete_sequence=['#43A047'])
            fig_lulus.update_traces(textposition='outside')
            st.plotly_chart(fig_lulus, use_container_width=True)
            
        # Baris Kedua: Grafik Garis Dinamika Seluruh Mahasiswa
        st.subheader("Dinamika Total Mahasiswa Aktif di Fakultas per Periode Semester")
        fig_aktif = px.line(active_per_period, x='Periode', y='Total Mahasiswa Aktif', 
                            markers=True, color_discrete_sequence=['#E53935'])
        fig_aktif.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_aktif, use_container_width=True)
        
        st.sidebar.success("✅ Data berhasil diproses sesuai format baru!")

    except Exception as e:
        st.error("❌ Terjadi kesalahan pembacaan dokumen. Pastikan Anda mengunggah dokumen 'PERKEMBANGAN MAHASISWA AKTIF DAN LULUSAN LENGKAP VOKASI.csv' dengan format pemisah (;) yang benar.")

else:
    st.info("👈 Silakan arahkan pandangan ke panel sebelah kiri. Klik tombol 'Browse files' untuk memasukkan dokumen data.")