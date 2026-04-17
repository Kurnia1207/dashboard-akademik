import streamlit as st
import pandas as pd
import plotly.express as px
import re

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Akademik Dinamis", layout="wide")

# -- PANEL ADMIN --
st.sidebar.header("⚙️ Panel Update Data")
st.sidebar.info("Upload langsung dokumen Master Excel (.xlsx). Sistem akan otomatis membaca semua sheet.")
uploaded_file = st.sidebar.file_uploader("📂 Upload Dokumen Excel (.xlsx)", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Membaca seluruh sheet di dalam file Excel
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        # Menyaring sheet: Sembunyikan sheet grafik bawaan
        valid_sheets = [s for s in sheet_names if "grafik" not in s.lower()]
        
        st.sidebar.markdown("---")
        selected_sheet = st.sidebar.selectbox("🔎 Pilih Lembar Kerja (Sheet)", valid_sheets)
        
        st.title(f"📊 Dashboard Akademik - {selected_sheet}")
        
        # Membaca mentah untuk memindai struktur
        df_raw = pd.read_excel(xls, sheet_name=selected_sheet, header=None)
        
        header_row = -1
        sheet_type = "unknown"
        
        for i, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper()
            if row_str.str.contains("TAHUN MASUK").any():
                header_row = i
                sheet_type = "cohort" 
                break
            elif row_str.str.contains("PRODI").any():
                header_row = i
                sheet_type = "summary" 
                break
                
        if header_row == -1:
            st.warning("⚠️ Format tabel tidak dikenali. Pastikan tabel memiliki kolom 'TAHUN MASUK' atau 'PRODI'.")
        else:
            # ==========================================
            # LOGIKA JIKA MEMBUKA SHEET DETAIL ANGKATAN
            # ==========================================
            if sheet_type == "cohort":
                row1 = df_raw.iloc[header_row].fillna("").astype(str).str.upper()
                row2 = df_raw.iloc[header_row + 1].fillna("").astype(str).str.upper()
                
                columns = []
                period_cols = []
                tahun_col, lulusan_col = None, None
                
                # Pemindai Kolom yang Jauh Lebih Luwes
                for col_idx in range(len(row1)):
                    val1 = row1[col_idx].strip()
                    val2 = row2[col_idx].strip()
                    
                    col_name = val2 if val2 != "" else val1
                    if col_name == "": col_name = f"Unnamed_{col_idx}"
                        
                    columns.append(col_name)
                    
                    if "TAHUN MASUK" in val1: 
                        tahun_col = col_name
                    elif re.search(r"\d{4}_\d", col_name): # Pemindai luwes mendeteksi tahun_semester
                        period_cols.append(col_name)
                    elif "LULUSAN" in val1 or "LULUSAN" in val2: 
                        lulusan_col = col_name
                        
                df_data = df_raw.iloc[header_row + 2:].copy()
                df_data.columns = columns
                
                df_data = df_data.dropna(subset=[tahun_col])
                df_data = df_data[df_data[tahun_col].astype(str).str.isnumeric()]
                
                for pc in period_cols: 
                    df_data[pc] = pd.to_numeric(df_data[pc], errors='coerce')
                if lulusan_col: 
                    df_data[lulusan_col] = pd.to_numeric(df_data[lulusan_col], errors='coerce')
                
                # Jika ada kolom periode terdeteksi, hitung MABA
                if len(period_cols) > 0:
                    df_data['MABA'] = df_data[period_cols].bfill(axis=1).iloc[:, 0]
                    aktif_per_periode = df_data[period_cols].sum(numeric_only=True).reset_index()
                    aktif_per_periode.columns = ['Periode', 'Total Aktif']
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Tren Mahasiswa Baru (MABA)")
                        fig_maba = px.bar(df_data, x=tahun_col, y='MABA', text='MABA', color_discrete_sequence=['#1E88E5'])
                        fig_maba.update_traces(textposition='outside')
                        st.plotly_chart(fig_maba, use_container_width=True)
                        
                    with col2:
                        if lulusan_col:
                            st.subheader("Total Lulusan per Angkatan")
                            fig_lulus = px.bar(df_data, x=tahun_col, y=lulusan_col, text=lulusan_col, color_discrete_sequence=['#43A047'])
                            fig_lulus.update_traces(textposition='outside')
                            st.plotly_chart(fig_lulus, use_container_width=True)
                            
                    st.subheader("Dinamika Mahasiswa Aktif per Semester")
                    fig_aktif = px.line(aktif_per_periode, x='Periode', y='Total Aktif', markers=True, color_discrete_sequence=['#E53935'])
                    fig_aktif.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_aktif, use_container_width=True)
                else:
                    st.error("Data semester tidak ditemukan. Pastikan format penulisan semester adalah 'Tahun_Semester' (Contoh: 2024_1).")

            # ==========================================
            # LOGIKA JIKA MEMBUKA SHEET TOTAL (SUMMARY)
            # ==========================================
            elif sheet_type == "summary":
                row1 = df_raw.iloc[header_row].fillna("").astype(str).str.upper()
                row2 = df_raw.iloc[header_row + 1].fillna("").astype(str).str.upper()
                
                columns, period_cols, prodi_col = [], [], None
                
                for col_idx in range(len(row1)):
                    val1 = row1[col_idx].strip()
                    val2 = row2[col_idx].strip()
                    
                    col_name = val2 if val2 != "" else val1
                    if col_name == "": col_name = f"Unnamed_{col_idx}"
                        
                    columns.append(col_name)
                    
                    if "PRODI" in val1: 
                        prodi_col = col_name
                    elif re.search(r"\d{4}_\d", col_name): # Pemindai luwes
                        period_cols.append(col_name)
                        
                df_data = df_raw.iloc[header_row + 2:].copy()
                df_data.columns = columns
                
                df_data = df_data.dropna(subset=[prodi_col])
                df_data = df_data[~df_data[prodi_col].astype(str).str.contains("TOTAL|JUMLAH", na=False, case=False)]
                
                if len(period_cols) > 0:
                    df_melt = df_data.melt(id_vars=[prodi_col], value_vars=period_cols, var_name='Periode', value_name='Lulusan')
                    df_melt['Lulusan'] = pd.to_numeric(df_melt['Lulusan'], errors='coerce').fillna(0)
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.subheader("Tren Kelulusan per Periode")
                        fig_bar = px.bar(df_melt, x='Periode', y='Lulusan', color=prodi_col, barmode='group')
                        st.plotly_chart(fig_bar, use_container_width=True)
                    with col2:
                        st.subheader("Proporsi Lulusan Keseluruhan")
                        jumlah_col = [c for c in df_data.columns if "JUMLAH" in c.upper()]
                        if jumlah_col:
                            fig_pie = px.pie(df_data, names=prodi_col, values=jumlah_col[0], hole=0.3)
                            st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.error("Data semester tidak terdeteksi. Pastikan format kolom periode benar (Contoh: 2017_2).")

        st.sidebar.success(f"✅ Sheet '{selected_sheet}' berhasil dimuat!")
        
    except Exception as e:
        st.error(f"❌ Terjadi kesalahan saat membaca dokumen: {str(e)}")

else:
    st.info("👈 Menunggu input. Silakan klik tombol 'Browse files' di sebelah kiri untuk mengunggah dokumen master Excel.")