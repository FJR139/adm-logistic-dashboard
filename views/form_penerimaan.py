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
    
    # KELUARKAN VARIABEL DARI FORM UNTUK VALIDASI REAL-TIME
    st.markdown("### 1. Pencatatan Flowmeter (Liter)")
    with st.container(border=True):
        col_in, col_out = st.columns(2)
        with col_in:
            st.write("**Flowmeter IN (Penerimaan)**")
            fm_in_before = st.number_input("Before (Awal) IN", min_value=0.0, format="%.0f", step=1.0, key="fm_in_b")
            fm_in_after = st.number_input("After (Akhir) IN", min_value=0.0, format="%.0f", step=1.0, key="fm_in_a")
            
        with col_out:
            st.write("**Flowmeter OUT**")
            fm_out_before = st.number_input("Before (Awal) OUT", min_value=0.0, format="%.0f", step=1.0, key="fm_out_b")
            fm_out_after = st.number_input("After (Akhir) OUT", min_value=0.0, format="%.0f", step=1.0, key="fm_out_a")

    st.markdown(f"### 2. Pencatatan Level Tangki ({lokasi_kap})")
    with st.container(border=True):
        col_t1, col_t2, col_daily = st.columns(3)
        with col_t1:
            st.write("**Tangki 1 (T.1)**")
            t1_before = st.number_input("T.1 Before", min_value=0.0, format="%.0f", step=1.0, key="t1_b")
            t1_after = st.number_input("T.1 After", min_value=0.0, format="%.0f", step=1.0, key="t1_a")
        
        with col_t2:
            st.write("**Tangki 2 (T.2)**")
            t2_before = st.number_input("T.2 Before", min_value=0.0, format="%.0f", step=1.0, key="t2_b")
            t2_after = st.number_input("T.2 After", min_value=0.0, format="%.0f", step=1.0, key="t2_a")

        with col_daily:
            st.write("**Daily Tank**")
            st.info("💡 Input otomatis dikali 2")
            daily_before = st.number_input("Daily Before (Input Asli)", min_value=0.0, format="%.0f", step=1.0, key="dt_b")
            daily_after = st.number_input("Daily After (Input Asli)", min_value=0.0, format="%.0f", step=1.0, key="dt_a")

    # ================= INDIKATOR PRA-SIMPAN (LIVE VALIDATION) =================
    vol_in = (fm_in_after - fm_in_before) if (fm_in_after and fm_in_before) else 0.0
    vol_out = (fm_out_after - fm_out_before) if (fm_out_after and fm_out_before) else 0.0
    
    # Hitung kenaikan total volume di tangki
    t_before_total = (t1_before or 0) + (t2_before or 0) + ((daily_before or 0) * 2)
    t_after_total = (t1_after or 0) + (t2_after or 0) + ((daily_after or 0) * 2)
    kenaikan_tangki = (t_after_total - t_before_total) + vol_out # Kenaikan fisik + yg dipompa keluar saat bongkar

    selisih_penerimaan = vol_in - kenaikan_tangki

    st.write("---")
    st.markdown("#### 🔍 Ringkasan Penerimaan & Validasi Selisih")
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.metric(label="Volume Flowmeter IN (Truk)", value=f"{vol_in:,.0f} L")
    with col_v2:
        st.metric(label="Kenaikan Level Tangki Aktual", value=f"{kenaikan_tangki:,.0f} L")
    with col_v3:
        if vol_in > 0:
            if abs(selisih_penerimaan) <= 10: # Toleransi 10 Liter
                st.metric(label="Selisih (Loss)", value=f"{selisih_penerimaan:,.0f} L", delta="Aman", delta_color="normal")
            else:
                st.metric(label="Selisih (Loss)", value=f"{selisih_penerimaan:,.0f} L", delta="PERINGATAN: CEK KEBOCORAN", delta_color="inverse")
        else:
             st.metric(label="Selisih (Loss)", value="0 L")

    # ================= TOMBOL SIMPAN =================
    st.write("")
    submitted = st.button("Simpan Data Penerimaan BBM", type="primary", use_container_width=True)
    
    if submitted:
        if vol_in < 0 or vol_out < 0:
            st.error("❌ Nilai 'After' tidak boleh lebih kecil dari 'Before' pada Flowmeter!")
        elif vol_in == 0:
            st.warning("⚠️ Volume masuk (Flowmeter IN) masih 0. Pastikan data sudah terisi.")
        elif conn is not None:
            try:
                cur = conn.cursor()
                
                # ... (Kueri INSERT ke log_penerimaan_tangki biarkan sama) ...
                cur.execute("DELETE FROM log_penerimaan_tangki WHERE tanggal = %s AND id_area = %s", (tgl_input, lokasi_kap))
                cur.execute("""
                    INSERT INTO log_penerimaan_tangki 
                    (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (tgl_input, lokasi_kap, 'GR', float(fm_in_before or 0), float(fm_in_after or 0), float(vol_in)))
                
                # ... (Kueri UPDATE ke daily_stock_log biarkan sama) ...
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
                    float(t1_after or 0), float(t2_after or 0), float((daily_after or 0) * 2), 
                    float(t_after_total), float(t_after_total)
                ))
                
                conn.commit()
                cur.close()
                
                # PESAN STATUS PASCA-SIMPAN YANG DIPERBARUI
                st.success(f"✅ Data Kedatangan BBM berhasil diperbarui! Volume Masuk Truk: **{vol_in:,.0f} L**")
                
                if abs(selisih_penerimaan) > 10:
                    st.error(f"⚠️ **PERINGATAN AUDIT:** Terdeteksi selisih sebesar **{selisih_penerimaan:,.0f} Liter** antara meteran truk dan kenaikan tangki pada {lokasi_kap}! Data telah disimpan dengan catatan anomali penerimaan.")
                
                st.toast("Data Bongkar Muat berhasil tersimpan!", icon="🚛")
                
            except Exception as e:
                conn.rollback()
                st.error(f"❌ Terjadi kesalahan saat menyimpan ke database: {e}")
        else:
            st.error("Koneksi database terputus.")