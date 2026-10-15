import streamlit as st
import pandas as pd
import datetime

def render_import_data(conn):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Import Data Historis (Excel / CSV)</h3>", unsafe_allow_html=True)
    st.write("---")
    
    st.info("💡 **Fitur ini digunakan untuk mengunggah data logistik bulan-bulan sebelumnya secara massal agar langsung terbaca di Grafik Analisis Tren.**")

    # ----------------------------------------
    # BAGIAN 1: DOWNLOAD TEMPLATE
    # ----------------------------------------
    st.markdown("#### 1. Unduh Template")
    st.write("Pastikan format kolom file yang Anda unggah sama persis dengan template CSV di bawah ini.")

    template_data = {
        "tanggal": ["2026-09-01", "2026-09-02"],
        "id_area": ["KAP-1", "KAP-2"],
        "stok_awal_level_meter": [12000, 15000],
        "total_pengisian": [8000, ""],
        "total_pemakaian": [2100, 1500],
        "stok_akhir_level_meter": [17900, 13500],
        "loss_kalkulasi": [-20, 15],
        "status_loss": ["AMAN", "AMAN"]
    }
    df_template = pd.DataFrame(template_data)
    csv_template = df_template.to_csv(index=False).encode('utf-8')

    st.download_button(
        label="📥 Download Template CSV",
        data=csv_template,
        file_name="Template_Import_Supabase.csv",
        mime="text/csv",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ----------------------------------------
    # BAGIAN 2: Upload & Preview Data
    # ----------------------------------------
    st.markdown("#### 2. Unggah File Data")
    uploaded_file = st.file_uploader("Pilih file CSV atau Excel (.xlsx)", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                if len(df.columns) == 1:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';')
            else:
                df = pd.read_excel(uploaded_file)
    
            st.success(f"✅ File {uploaded_file.name} berhasil dibaca!")

            st.markdown("**Preview Data:** (Menampilkan 5 baris pertama)")
            st.dataframe(df.head())

            # ----------------------------------------
            # BAGIAN 3: EKSEKUSI KE DATABASE
            # ----------------------------------------
            if st.button("🚀 Simpan ke Database Supabase", type="primary"):
                with st.spinner("Sedang memproses dan menyimpan data massal..."):
                    if conn is not None:
                        cur = conn.cursor()
                        sukses = 0
                        gagal = 0

                        for index, row in df.iterrows():
                            try:
                                tgl_val = pd.to_datetime(row['tanggal']).strftime('%Y-%m-%d')

                                s_awal = None if pd.isna(row['stok_awal_level_meter']) else float(row['stok_awal_level_meter'])
                                t_isi = None if pd.isna(row['total_pengisian']) else float(row['total_pengisian'])
                                t_pakai = None if pd.isna(row['total_pemakaian']) else float(row['total_pemakaian'])
                                s_akhir = None if pd.isna(row['stok_akhir_level_meter']) else float(row['stok_akhir_level_meter'])
                                loss = None if pd.isna(row['loss_kalkulasi']) else float(row['loss_kalkulasi'])
                                status = None if pd.isna(row['status_loss']) else str(row['status_loss'])
                                id_area = str(row['id_area'])

                                cur.execute("""
                                    INSERT INTO daily_stock_log
                                    (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (tanggal, id_area) DO UPDATE
                                    SET stok_awal_level_meter = EXCLUDED.stok_awal_level_meter,
                                    total_pengisian = EXCLUDED.total_pengisian,
                                    total_pemakaian = EXCLUDED.total_pemakaian,
                                    stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter,
                                    loss_kalkulasi = EXCLUDED.loss_kalkulasi,
                                    status_loss = EXCLUDED.status_loss;
                                """, (tgl_val, id_area, s_awal, t_isi, t_pakai, s_akhir, loss, status))

                                sukses += 1
                            except Exception as row_error:
                                gagal += 1

                        conn.commit()
                        cur.close()

                        if gagal == 0:
                            st.success(f"🎉 Berhasil! {sukses} baris data berhasil diimpor ke database.")
                            st.toast("✅ Data berhasil diimpor ke sistem!", icon="💾")
                        else: 
                            st.warning(f"Selesai dengan catatan: {sukses} baris berhasil diimpor, {gagal} baris gagal (mungkin format data salah).")
                    else:
                        st.error("Koneksi database terputus.")

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat memproses file: {e}")