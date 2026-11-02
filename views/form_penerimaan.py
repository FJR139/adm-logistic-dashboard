import streamlit as st
import datetime

def render_penerimaan(conn, role="Logistik"):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Penerimaan BBM (Bongkar Muat)</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #005A9E;'>Masuk sebagai: <b>{role.upper()}</b></p>", unsafe_allow_html=True)
    st.write("---")

    if role not in ["Logistik"]:
        st.warning("🔒 Halaman ini khusus untuk pencatatan kedatangan BBM oleh Tim Logistik.")
        return

    st.info("🚛 Pencatatan nilai Sebelum (Before) dan Sesudah (After) pembongkaran truk tangki.")
    
    col_tgl, col_lok = st.columns(2)
    with col_tgl:
        tgl_input = st.date_input("Tanggal Kedatangan", value=datetime.date.today())
    with col_lok:
        lokasi_kap = st.radio("Lokasi Pembongkaran:", ["KAP-1", "KAP-2"], horizontal=True)
    
    with st.form("form_bongkar_muat"):
        st.markdown("### 1. Pencatatan Flowmeter (Liter)")
        
        col_in, col_out = st.columns(2)
        with col_in:
            st.write("**Flowmeter IN (Penerimaan)**")
            fm_in_before = st.number_input("Before (Awal) IN", min_value=0.0, format="%.0f", step=1.0)
            fm_in_after = st.number_input("After (Akhir) IN", min_value=0.0, format="%.0f", step=1.0)
            
        with col_out:
            st.write("**Flowmeter OUT**")
            fm_out_before = st.number_input("Before (Awal) OUT", min_value=0.0, format="%.0f", step=1.0)
            fm_out_after = st.number_input("After (Akhir) OUT", min_value=0.0, format="%.0f", step=1.0)

        st.markdown(f"### 2. Pencatatan Level Tangki ({lokasi_kap})")
        col_t1, col_t2, col_daily = st.columns(3)
        with col_t1:
            st.write("**Tangki 1 (T.1)**")
            t1_before = st.number_input("T.1 Before", min_value=0.0, format="%.0f", step=1.0)
            t1_after = st.number_input("T.1 After", min_value=0.0, format="%.0f", step=1.0)
        
        with col_t2:
            st.write("**Tangki 2 (T.2)**")
            t2_before = st.number_input("T.2 Before", min_value=0.0, format="%.0f", step=1.0)
            t2_after = st.number_input("T.2 After", min_value=0.0, format="%.0f", step=1.0)

        with col_daily:
            st.write("**Daily Tank**")
            st.info("💡 Input otomatis dikali 2 saat disimpan.")
            daily_before = st.number_input("Daily Before (Input Asli)", min_value=0.0, format="%.0f", step=1.0)
            daily_after = st.number_input("Daily After (Input Asli)", min_value=0.0, format="%.0f", step=1.0)

        st.write("---")
        submitted = st.form_submit_button("Simpan Data Penerimaan BBM", type="primary", use_container_width=True)
        
        if submitted:
            vol_in = fm_in_after - fm_in_before
            vol_out = fm_out_after - fm_out_before
            
            # Perkalian otomatis (x2) untuk Daily Tank
            daily_tank_actual_after = daily_after * 2
            total_storage_after = t1_after + t2_after + daily_tank_actual_after
            
            if vol_in < 0 or vol_out < 0:
                st.error("❌ Nilai 'After' tidak boleh lebih kecil dari 'Before' pada Flowmeter!")
            elif vol_in == 0:
                st.warning("⚠️ Volume masuk (Flowmeter IN) masih 0. Pastikan data sudah terisi.")
            elif conn is not None:
                # ... (lanjutkan eksekusi kueri database Anda) ...
                try:
                    cur = conn.cursor()
                    
                    cur.execute("DELETE FROM log_penerimaan_tangki WHERE tanggal = %s AND id_area = %s", (tgl_input, lokasi_kap))
                    
                    cur.execute("""
                        INSERT INTO log_penerimaan_tangki 
                        (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (tgl_input, lokasi_kap, 'GR', float(fm_in_before), float(fm_in_after), float(vol_in)))
                    
                    cur.execute("""
                        INSERT INTO daily_stock_log (
                            tanggal, id_area, total_pengisian, 
                            tank1_level, tank2_level, daily_tank_level, 
                            total_storage_level, stok_akhir_level_meter
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (tanggal, id_area) 
                        DO UPDATE SET 
                            total_pengisian = EXCLUDED.total_pengisian,
                            tank1_level = EXCLUDED.tank1_level,
                            tank2_level = EXCLUDED.tank2_level,
                            daily_tank_level = EXCLUDED.daily_tank_level,
                            total_storage_level = EXCLUDED.total_storage_level,
                            stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter;
                    """, (
                        tgl_input, lokasi_kap, float(vol_in), 
                        float(t1_after), float(t2_after), float(daily_tank_actual_after), 
                        float(total_storage_after), float(total_storage_after)
                    ))
                    
                    conn.commit()
                    cur.close()
                    
                    st.success(f"✅ Data Kedatangan BBM berhasil diperbarui! Volume Masuk: {vol_in:,.0f} Liter ditetapkan untuk {lokasi_kap} pada {tgl_input.strftime('%d %b %Y')}.")
                    st.toast("Data Bongkar Muat berhasil tersimpan!", icon="🚛")
                    
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan saat menyimpan ke database: {e}")
            else:
                st.error("Koneksi database terputus.")