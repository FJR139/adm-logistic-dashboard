import streamlit as st
import datetime
from utils import get_stok_awal

def render_kap1(conn):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Input Data Harian - KAP-1</h3>", unsafe_allow_html=True)
    st.write("---")

    # --- Input Tanggal ---
    col_date, spacer = st.columns([3, 5])
    with col_date:
        st.markdown("### 🗓️ Tanggal")
        tgl_input = st.date_input(
            "Tanggal",
            value=datetime.date.today(),
            max_value=datetime.date.today(),
            label_visibility="collapsed"
        )
    st.write("")
    
    stok_awal_kemarin = get_stok_awal(conn, "KAP-1", tgl_input)

    col_kiri, spacer, col_kanan = st.columns([10, 1, 10])

    with col_kiri:
        st.markdown("### 1. Penerimaan (FM1)")
        with st.container(border=True):
            f1_awal_in = st.number_input("Digit Awal (Liter) FM1", min_value=0.0, format="%.0f", key="kap1_f1_a", step=1.0, value=None)
            f1_akhir_in = st.number_input("Digit Akhir (Liter) FM1", min_value=0.0, format="%.0f", key="kap1_f1_b", step=1.0, value=None)
            
            f1_awal = f1_awal_in if f1_awal_in is not None else 0.0
            f1_akhir = f1_akhir_in if f1_akhir_in is not None else 0.0
            volume_f1 = f1_akhir - f1_awal
            st.info(f"✅ **Volume Masuk (FM1):** {volume_f1:,.0f} Liter")

        st.markdown("### 2. Transfer Internal (FM2)")
        with st.container(border=True):
            fm2_awal_in = st.number_input("Digit Awal FM2 (Liter)", min_value=0.0, format="%.0f", key="kap1_fm2_a", step=1.0, value=None)
            fm2_akhir_in = st.number_input("Digit Akhir FM2 (Liter)", min_value=0.0, format="%.0f", key="kap1_fm2_b", step=1.0, value=None)
            
            fm2_awal = fm2_awal_in if fm2_awal_in is not None else 0.0
            fm2_akhir = fm2_akhir_in if fm2_akhir_in is not None else 0.0
            volume_fm2 = fm2_akhir - fm2_awal
            st.info(f"✅ **Volume Transfer (FM2):** {volume_fm2:,.0f} Liter")

        st.markdown("### 3. Level Meter")
        col1, col2 = st.columns(2)
    
        with col1:
            tank1_input = st.number_input("Tanki 1 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
            tank2_input = st.number_input("Tanki 2 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
            daily_tank_input = st.number_input("Daily Tank (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
        
        val_tank1 = tank1_input if tank1_input is not None else 0.0
        val_tank2 = tank2_input if tank2_input is not None else 0.0
        val_daily = daily_tank_input if daily_tank_input is not None else 0.0
        
        daily_tank_actual = val_daily * 2
        total_storage = val_tank1 + val_tank2 + daily_tank_actual

        with col2:
            st.write("### Total Kalkulasi")
            st.metric(label="Total Storage (Liter)", value=f"{total_storage:.1f}")
            st.info(f"💡 Info: Nilai Daily Tank otomatis dikali 2 ({val_daily} x 2 = {daily_tank_actual})")

    # ================= KOLOM KANAN =================
    with col_kanan:
        st.markdown("### 4. Dispenser Reguler (Pompa RH & LH)")
        
        # Tabs masuk
        tab_shift_a, tab_shift_b = st.tabs(["⚙️ SHIFT A", "⚙️ SHIFT B"])

        # ----- SHIFT A -----
        with tab_shift_a:
            st.write("#### Pengeluaran Shift A")
            col_rh_a, col_lh_a = st.columns(2)

            with col_rh_a:
                st.write("**Pompa RH**")
                with st.container(border=True):
                    rh_a_awal_in = st.number_input("Digit Awal RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_awal", step=1.0, value=None)
                    rh_a_akhir_in = st.number_input("Digit Akhir RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_akhir", step=1.0, value=None)        
                    rh_a_awal = rh_a_awal_in if rh_a_awal_in is not None else 0.0
                    rh_a_akhir = rh_a_akhir_in if rh_a_akhir_in is not None else 0.0
                    vol_rh_a = rh_a_akhir - rh_a_awal
                    st.info(f"✅ **Volume Keluar RH(A):** {vol_rh_a:,.0f} Liter")

            with col_lh_a:
                st.write("**Pompa LH**")
                with st.container(border=True):
                    lh_a_awal_in = st.number_input("Digit Awal LH (A)", min_value=0.0, format="%.0f", key="kap1_lh_a_awal", step=1.0, value=None)
                    lh_a_akhir_in = st.number_input("Digit Akhir LH (A)", min_value=0.0, format="%.0f", key="kap1_lh_a_akhir", step=1.0, value=None)
                    lh_a_awal = lh_a_awal_in if lh_a_awal_in is not None else 0.0
                    lh_a_akhir = lh_a_akhir_in if lh_a_akhir_in is not None else 0.0
                    vol_lh_a = lh_a_akhir - lh_a_awal
                    st.info(f"✅ **Volume Keluar RH(A):** {vol_rh_a:,.0f} Liter")

        # ----- SHIFT B -----
        with tab_shift_b:
            st.write("#### Pengeluaran Shift B")
            col_rh_b, col_lh_b = st.columns(2)

            with col_rh_b:
                st.write("**Pompa RH**")
                with st.container(border=True):
                    rh_b_awal_in = st.number_input("Digit Awal RH (B)", min_value=0.0, format="%.0f", key="kap1_rh_b_awal", step=1.0, value=None)
                    rh_b_akhir_in = st.number_input("Digit Akhir RH (B)", min_value=0.0, format="%.0f", key="kap1_rh_b_akhir", step=1.0, value=None)
                    rh_b_awal = rh_b_awal_in if rh_b_awal_in is not None else 0.0
                    rh_b_akhir = rh_b_akhir_in if rh_b_akhir_in is not None else 0.0
                    vol_rh_b = rh_b_akhir - rh_b_awal
                    st.info(f"✅ **Volume Keluar RH(A):** {vol_rh_a:,.0f} Liter")

            with col_lh_b:
                st.write("**Pompa LH**")
                with st.container(border=True):
                    lh_b_awal_in = st.number_input("Digit Awal LH (B)", min_value=0.0, format="%.0f", key="kap1_lh_b_awal", step=1.0, value=None)
                    lh_b_akhir_in = st.number_input("Digit Akhir LH (B)", min_value=0.0, format="%.0f", key="kap1_lh_b_akhir", step=1.0, value=None)
                    lh_b_awal = lh_b_awal_in if lh_b_awal_in is not None else 0.0
                    lh_b_akhir = lh_b_akhir_in if lh_b_akhir_in is not None else 0.0
                    vol_lh_b = lh_b_akhir - lh_b_awal
                    st.info(f"✅ **Volume Keluar RH(A):** {vol_rh_a:,.0f} Liter")

        # Kalkulasi Total
        total_volume_reguler = vol_rh_a + vol_lh_a + vol_rh_b + vol_lh_b
        st.info(f"**Total Volume Reguler (Seluruh Shift & Pompa): {total_volume_reguler:.2f} Liter**") 

        st.markdown("### 5. Dispenser Non-Reguler (F5)")
        with st.container(border=True):
            f5_total_in = st.number_input("Total Volume (Liter) RnD", min_value=0.0, format="%.0f", key="kap1_f5_total", step=1.0, value=None)
            volume_f5 = f5_total_in if f5_total_in is not None else 0.0
            st.info(f"✅ **Volume Keluar Non-Reguler:** {volume_f5:,.0f} Liter")
            
        st.subheader("6. Totalisator OUT ASSY")
        tot_out_in = st.number_input("Input Totalisator OUT ASSY", min_value=0.0, format="%.0f", step=1.0, value=None)
        totalisator_out_assy_input = tot_out_in if tot_out_in is not None else 0.0

    st.write("---")
    
    # ================= DATABASE =================
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        if st.button("SUBMIT DATA HARIAN KAP-1", use_container_width=True, type="primary", key="kap1_submit"):
            # Validasi agar angka akhir tidak lebih kecil dari awal
            if volume_f1 < 0 or volume_fm2 < 0 or vol_rh_a < 0 or vol_lh_a < 0 or vol_rh_b < 0 or vol_lh_b < 0:
                st.error("❌ Digit akhir tidak boleh lebih kecil dari digit awal! Periksa kembali inputan Anda.")
            elif conn is not None:
                try:
                    cur = conn.cursor()

                    # 1. Simpan Penerimaan Tangki (FM1)
                    cur.execute("""INSERT INTO log_penerimaan_tangki (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-1', 'GR', f1_awal, f1_akhir, volume_f1))

                    # 2. Simpan Transfer Internal (FM2)
                    cur.execute("""INSERT INTO log_transfer_internal (tanggal, id_area, fm2_awal, fm2_akhir, volume_transfer)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (tgl_input, 'KAP-1', fm2_awal, fm2_akhir, volume_fm2))

                    # 3. Simpan Dispenser Reguler
                    data_dispenser = [
                        ('RH (Shift A)', rh_a_awal, rh_a_akhir, vol_rh_a),
                        ('LH (Shift A)', lh_a_awal, lh_a_akhir, vol_lh_a),
                        ('RH (Shift B)', rh_b_awal, rh_b_akhir, vol_rh_b),
                        ('LH (Shift B)', lh_b_awal, lh_b_akhir, vol_lh_b)
                    ]
                    
                    for nama_pompa, aw, ak, vol in data_dispenser:
                        cur.execute("""INSERT INTO log_pengeluaran_dispenser 
                                       (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-1', 'GI Reguler', nama_pompa, aw, ak, vol))

                    # 4. Simpan Dispenser Non-Reguler (F5)
                    if volume_f5 > 0:
                        cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-1', 'GI Non-Reguler', 'F5', 0, 0, volume_f5))
                    
                    # 5. Kalkulasi Loss & Simpan
                    total_pakai = total_volume_reguler + volume_f5
                    stok_akhir_aktual = total_storage
                    stok_awal_aktual = get_stok_awal(conn, 'KAP-1', tgl_input)
                    loss = round((stok_awal_aktual + volume_f1 - total_pakai) - stok_akhir_aktual, 2)
                    status_loss = "SELISIH" if abs(loss) > 0.01 else "AMAN"

                    cur.execute("""INSERT INTO daily_stock_log
                                   (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss, tank1_level, tank2_level, daily_tank_level, total_storage_level, totalisator_out_assy)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                   ON CONFLICT (tanggal, id_area) DO UPDATE SET
                                   stok_awal_level_meter = EXCLUDED.stok_awal_level_meter,
                                   total_pengisian = EXCLUDED.total_pengisian,
                                   total_pemakaian = EXCLUDED.total_pemakaian,
                                   stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter,
                                   loss_kalkulasi = EXCLUDED.loss_kalkulasi,
                                   status_loss = EXCLUDED.status_loss,
                                   tank1_level = EXCLUDED.tank1_level,
                                   tank2_level = EXCLUDED.tank2_level,
                                   daily_tank_level = EXCLUDED.daily_tank_level,
                                   total_storage_level = EXCLUDED.total_storage_level,
                                   totalisator_out_assy = EXCLUDED.totalisator_out_assy;""",
                                (
                                tgl_input, 'KAP-1',
                                float(round(stok_awal_aktual, 2)), float(round(volume_f1, 2)),
                                float(round(total_pakai, 2)), float(round(stok_akhir_aktual, 2)),
                                float(round(loss, 2)), status_loss,
                                float(val_tank1), float(val_tank2), float(daily_tank_actual), float(total_storage), float(totalisator_out_assy_input)
                                ))
                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-1 tanggal {tgl_input.strftime('%d %B %Y')} berhasil disimpan!")
                    st.toast("✅ Data KAP-1 berhasil disimpan ke sistem!", icon="💾")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database: {e}")
            else:
                st.error("Koneksi database terputus.")