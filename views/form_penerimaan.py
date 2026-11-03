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
    
    st.markdown("### 1. Pencatatan Flowmeter (Liter)")
    with st.container(border=True):
        col_in, col_out = st.columns(2)
        with col_in:
            st.write("**Flowmeter IN (Penerimaan)**")
            fm_in_before = st.number_input("Before (Awal) IN", min_value=0.0, format="%.0f", step=1.0, value=None, key="fm_in_b")
            fm_in_after = st.number_input("After (Akhir) IN", min_value=0.0, format="%.0f", step=1.0, value=None, key="fm_in_a")
            
        with col_out:
            st.write("**Flowmeter OUT**")
            fm_out_before = st.number_input("Before (Awal) OUT", min_value=0.0, format="%.0f", step=1.0, value=None, key="fm_out_b")
            fm_out_after = st.number_input("After (Akhir) OUT", min_value=0.0, format="%.0f", step=1.0, value=None, key="fm_out_a")

    st.markdown(f"### 2. Pencatatan Level Tangki ({lokasi_kap})")
    with st.container(border=True):
        col_t1, col_t2, col_daily = st.columns(3)
        with col_t1:
            st.write("**Tangki 1 (T.1)**")
            t1_before = st.number_input("T.1 Before", min_value=0.0, format="%.0f", step=1.0, value=None, key="t1_b")
            t1_after = st.number_input("T.1 After", min_value=0.0, format="%.0f", step=1.0, value=None, key="t1_a")
        
        with col_t2:
            st.write("**Tangki 2 (T.2)**")
            t2_before = st.number_input("T.2 Before", min_value=0.0, format="%.0f", step=1.0, value=None, key="t2_b")
            t2_after = st.number_input("T.2 After", min_value=0.0, format="%.0f", step=1.0, value=None, key="t2_a")

        with col_daily:
            st.write("**Daily Tank**")
            st.info("💡 Input otomatis dikali 2")
            daily_before = st.number_input("Daily Before (Input Asli)", min_value=0.0, format="%.0f", step=1.0, value=None, key="dt_b")
            daily_after = st.number_input("Daily After (Input Asli)", min_value=0.0, format="%.0f", step=1.0, value=None, key="dt_a")

    # ================= FILTER NILAI KOSONG & INDIKATOR PRA-SIMPAN =================
    val_fm_in_b = fm_in_before if fm_in_before is not None else 0.0
    val_fm_in_a = fm_in_after if fm_in_after is not None else 0.0
    val_fm_out_b = fm_out_before if fm_out_before is not None else 0.0
    val_fm_out_a = fm_out_after if fm_out_after is not None else 0.0
    
    val_t1_b = t1_before if t1_before is not None else 0.0
    val_t1_a = t1_after if t1_after is not None else 0.0
    val_t2_b = t2_before if t2_before is not None else 0.0
    val_t2_a = t2_after if t2_after is not None else 0.0
    val_dt_b = daily_before if daily_before is not None else 0.0
    val_dt_a = daily_after if daily_after is not None else 0.0

    vol_in = val_fm_in_a - val_fm_in_b
    vol_out = val_fm_out_a - val_fm_out_b
    
    t_before_total = val_t1_b + val_t2_b + (val_dt_b * 2)
    t_after_total = val_t1_a + val_t2_a + (val_dt_a * 2)
    kenaikan_tangki = (t_after_total - t_before_total) + vol_out 

    selisih_penerimaan = vol_in - kenaikan_tangki

    # --- UI KARTU KPI RINGKASAN ---
    st.write("---")
    st.markdown("#### 🔍 Ringkasan Penerimaan & Validasi Selisih")
    
    # Logika Warna Dinamis untuk Kartu Selisih
    if vol_in == 0:
        s_color = "#64748B" # Abu-abu (Belum ada input)
        s_bg = "#F8FAFC"
        s_status = "Menunggu Input Data..."
    elif abs(selisih_penerimaan) <= 10:
        s_color = "#10B981" # Hijau (Aman)
        s_bg = "#ECFDF5"
        s_status = "✅ STATUS AMAN"
    else:
        s_color = "#EF4444" # Merah (Peringatan)
        s_bg = "#FEF2F2"
        s_status = "⚠️ PERINGATAN: CEK KEBOCORAN!"

    # Template HTML Kartu
    kpi_card_html = """
    <div style="background-color: {bg}; border-left: 5px solid {border}; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); height: 100%;">
        <p style="margin: 0; font-size: 13px; color: #64748B; font-weight: 700; text-transform: uppercase;">{title}</p>
        <h3 style="margin: 6px 0 0 0; color: #1E293B; font-size: 26px;">{value:,.0f} L</h3>
        <p style="margin: 6px 0 0 0; font-size: 12px; font-weight: 700; color: {border};">{status}</p>
    </div>
    """

    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        st.markdown(kpi_card_html.format(
            bg="#F0F9FF", border="#0EA5E9", title="Volume Flowmeter IN (Truk)", 
            value=vol_in, status="Data Masuk Aktual"
        ), unsafe_allow_html=True)
    with col_v2:
        st.markdown(kpi_card_html.format(
            bg="#F3F4F6", border="#6B7280", title="Kenaikan Tangki Aktual", 
            value=kenaikan_tangki, status="T1 + T2 + (Daily x 2)"
        ), unsafe_allow_html=True)
    with col_v3:
        st.markdown(kpi_card_html.format(
            bg=s_bg, border=s_color, title="Selisih (Loss)", 
            value=selisih_penerimaan, status=s_status
        ), unsafe_allow_html=True)

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
                
                cur.execute("DELETE FROM log_penerimaan_tangki WHERE tanggal = %s AND id_area = %s", (tgl_input, lokasi_kap))
                cur.execute("""
                    INSERT INTO log_penerimaan_tangki 
                    (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (tgl_input, lokasi_kap, 'GR', float(val_fm_in_b), float(val_fm_in_a), float(vol_in)))
                
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
                    float(val_t1_a), float(val_t2_a), float(val_dt_a * 2), 
                    float(t_after_total), float(t_after_total)
                ))
                
                conn.commit()
                cur.close()
                
                st.success(f"✅ Data Kedatangan BBM berhasil diperbarui! Volume Masuk Truk: **{vol_in:,.0f} L**")
                
                if abs(selisih_penerimaan) > 10:
                    st.error(f"⚠️ **PERINGATAN AUDIT:** Terdeteksi selisih sebesar **{selisih_penerimaan:,.0f} Liter** antara meteran truk dan kenaikan tangki pada {lokasi_kap}! Data telah disimpan dengan catatan anomali penerimaan.")
                
                st.toast("Data Bongkar Muat berhasil tersimpan!", icon="🚛")
                
            except Exception as e:
                conn.rollback()
                st.error(f"❌ Terjadi kesalahan saat menyimpan ke database: {e}")
        else:
            st.error("Koneksi database terputus.")