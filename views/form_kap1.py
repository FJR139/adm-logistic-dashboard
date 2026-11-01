import streamlit as st
import datetime
from utils import get_stok_awal

def render_kap1(conn, role="Logistik", mode=None):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Input Data Harian - KAP-1</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #005A9E;'>Masuk sebagai: <b>{role.upper()}</b></p>", unsafe_allow_html=True)
    st.write("---")

    col_date, spacer = st.columns([3, 5])
    with col_date:
        st.markdown("### 🗓️ Tanggal")
        tgl_input = st.date_input("Tanggal", value=datetime.date.today(), max_value=datetime.date.today(), label_visibility="collapsed")
    st.write("")
    
    stok_awal_kemarin = get_stok_awal(conn, "KAP-1", tgl_input)

    # --- INISIALISASI VARIABEL DEFAULT (PENTING AGAR DATABASE TIDAK ERROR) ---
    volume_f1 = 0.0; f1_awal = 0.0; f1_akhir = 0.0 
    volume_fm2 = 0.0; fm2_awal = 0.0; fm2_akhir = 0.0
    val_tank1 = 0.0; val_tank2 = 0.0; val_daily = 0.0; daily_tank_actual = 0.0; total_storage = 0.0
    vol_rh_a = 0.0; rh_a_awal = 0.0; rh_a_akhir = 0.0
    vol_lh_a = 0.0; lh_a_awal = 0.0; lh_a_akhir = 0.0
    vol_rh_b = 0.0; rh_b_awal = 0.0; rh_b_akhir = 0.0
    vol_lh_b = 0.0; lh_b_awal = 0.0; lh_b_akhir = 0.0
    volume_f5 = 0.0; total_volume_reguler = 0.0; total_pakai = 0.0
    totalisator_out_assy_input = 0.0; tot_out_awal = 0.0; tot_out_akhir = 0.0

    # ================= STRUKTUR TAB DAILY INPUT =================
    if mode == "Daily":
        tab_logistik, tab_produksi = st.tabs(["🧑‍🔧 Tim Logistik", "⚙️ Tim Produksi"])
        
        # --- TAB MILIK LOGISTIK ---
        with tab_logistik:
            if role in ["Logistik"]:
                st.markdown("### 1. Level Meter Tangki (Awal Shift)")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    with st.container(border=True):
                        tank1_input = st.number_input("Tanki 1 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tank2_input = st.number_input("Tanki 2 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        daily_tank_input = st.number_input("Daily Tank (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        
                        val_tank1 = tank1_input if tank1_input is not None else 0.0
                        val_tank2 = tank2_input if tank2_input is not None else 0.0
                        val_daily = daily_tank_input if daily_tank_input is not None else 0.0
                        daily_tank_actual = val_daily * 2
                        total_storage = val_tank1 + val_tank2 + daily_tank_actual
                with col_t2:
                    st.info(f"💡 Info: Nilai Daily Tank otomatis dikali 2\n\n**Total Storage:** {total_storage:,.0f} Liter")

                st.markdown("### 2. Dispenser Non-Reguler (R&D) & Totalisator")
                col_f5, col_tot = st.columns(2)
                with col_f5:
                    with st.container(border=True):
                        f5_total_in = st.number_input("Total Volume RnD (F5)", min_value=0.0, format="%.0f", key="kap1_f5", step=1.0, value=None)
                        volume_f5 = f5_total_in if f5_total_in is not None else 0.0
                with col_tot:
                    with st.container(border=True):
                        tot_out_awal_in = st.number_input("Awal Totalisator", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tot_out_akhir_in = st.number_input("Akhir Totalisator", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tot_out_awal = tot_out_awal_in if tot_out_awal_in is not None else 0.0
                        tot_out_akhir = tot_out_akhir_in if tot_out_akhir_in is not None else 0.0
                        totalisator_out_assy_input = tot_out_akhir - tot_out_awal
            else:
                st.warning("🔒 Area ini khusus untuk Tim Logistik.")

        # --- TAB MILIK PRODUKSI ---
        with tab_produksi:
            if role in ["Produksi", "Logistik"]:
                st.markdown("### 3. Dispenser Jalur Produksi")
                tab_shift_a, tab_shift_b = st.tabs(["⚙️ SHIFT A", "⚙️ SHIFT B"])

                with tab_shift_a:
                    col_rh_a, col_lh_a = st.columns(2)
                    with col_rh_a:
                        st.write("**Pompa RH**")
                        with st.container(border=True):
                            rh_a_awal_in = st.number_input("Digit Awal RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_awal", step=1.0, value=None)
                            rh_a_akhir_in = st.number_input("Digit Akhir RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_akhir", step=1.0, value=None)        
                            rh_a_awal = rh_a_awal_in if rh_a_awal_in is not None else 0.0
                            rh_a_akhir = rh_a_akhir_in if rh_a_akhir_in is not None else 0.0
                            vol_rh_a = rh_a_akhir - rh_a_awal
                    with col_lh_a:
                        st.write("**Pompa LH**")
                        with st.container(border=True):
                            lh_a_awal_in = st.number_input("Digit Awal LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_awal", step=1.0, value=None)
                            lh_a_akhir_in = st.number_input("Digit Akhir LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_akhir", step=1.0, value=None)
                            lh_a_awal = lh_a_awal_in if lh_a_awal_in is not None else 0.0
                            lh_a_akhir = lh_a_akhir_in if lh_a_akhir_in is not None else 0.0
                            vol_lh_a = lh_a_akhir - lh_a_awal

                with tab_shift_b:
                    col_rh_b, col_lh_b = st.columns(2)
                    with col_rh_b:
                        st.write("**Pompa RH**")
                        with st.container(border=True):
                            rh_b_awal_in = st.number_input("Digit Awal RH(B)", min_value=0.0, format="%.0f", key="kap1_rh_b_awal", step=1.0, value=None)
                            rh_b_akhir_in = st.number_input("Digit Akhir RH(B)", min_value=0.0, format="%.0f", key="kap1_rh_b_akhir", step=1.0, value=None)
                            rh_b_awal = rh_b_awal_in if rh_b_awal_in is not None else 0.0
                            rh_b_akhir = rh_b_akhir_in if rh_b_akhir_in is not None else 0.0
                            vol_rh_b = rh_b_akhir - rh_b_awal
                    with col_lh_b:
                        st.write("**Pompa LH**")
                        with st.container(border=True):
                            lh_b_awal_in = st.number_input("Digit Awal LH(B)", min_value=0.0, format="%.0f", key="kap1_lh_b_awal", step=1.0, value=None)
                            lh_b_akhir_in = st.number_input("Digit Akhir LH(B)", min_value=0.0, format="%.0f", key="kap1_lh_b_akhir", step=1.0, value=None)
                            lh_b_awal = lh_b_awal_in if lh_b_awal_in is not None else 0.0
                            lh_b_akhir = lh_b_akhir_in if lh_b_akhir_in is not None else 0.0
                            vol_lh_b = lh_b_akhir - lh_b_awal

                total_volume_reguler = vol_rh_a + vol_lh_a + vol_rh_b + vol_lh_b
            else:
                st.warning("🔒 Area khusus Tim Produksi.")

    # ================= PRE-SUBMIT LIVE VALIDATION (OPSI 3) =================
    st.write("---")
    
    ex_isi_prev = 0.0; ex_stok_prev = 0.0; ex_pakai_prev = 0.0
    if conn:
        try:
            c_check = conn.cursor()
            c_check.execute("SELECT total_pengisian, total_pemakaian, stok_akhir_level_meter FROM daily_stock_log WHERE tanggal = %s AND id_area = 'KAP-1'", (tgl_input,))
            row_prev = c_check.fetchone()
            if row_prev:
                ex_isi_prev = float(row_prev[0]) if row_prev[0] is not None else 0.0
                ex_pakai_prev = float(row_prev[1]) if row_prev[1] is not None else 0.0
                ex_stok_prev = float(row_prev[2]) if row_prev[2] is not None else 0.0
            c_check.close()
        except:
            pass

    sim_isi = volume_f1 if role in ["Maintenance", "Logistik"] else ex_isi_prev
    sim_stok = total_storage if (role in ["Maintenance", "Logistik"] and total_storage > 0) else ex_stok_prev
    sim_reguler = total_volume_reguler if role in ["Produksi", "Logistik"] else (ex_pakai_prev - ex_isi_prev if ex_pakai_prev > 0 else 0.0)
    sim_f5 = volume_f5 if role in ["Maintenance", "Logistik"] else 0.0
    sim_pakai = sim_reguler + sim_f5 if (role in ["Produksi", "Logistik"] or sim_f5 > 0) else ex_pakai_prev
    
    stok_awal_calc = stok_awal_kemarin if stok_awal_kemarin is not None else 0.0
    
    if sim_stok > 0 or sim_pakai > 0 or sim_isi > 0:
        est_loss = round((stok_awal_calc + sim_isi - sim_pakai) - sim_stok, 2)
        col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
        with col_v2:
            if abs(est_loss) <= 0.01:
                st.success(f"🔍 Validasi Pre-Submit: STATUS BALANCE / AMAN (Loss: {est_loss:,.1f} L)")
            elif abs(est_loss) > 1000:
                st.error(f"⚠️ PERINGATAN: SELISIH SANGAT BESAR (Loss: {est_loss:,.1f} L)")
            else:
                st.warning(f"ℹ️ Estimasi Selisih Terdeteksi (Loss: {est_loss:,.1f} L)")

    # ================= STEP 3: DATABASE MERGING & SUBMIT =================
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        if st.button("SUBMIT DATA HARIAN KAP-1", use_container_width=True, type="primary", key="kap1_submit"):
            err_maint = (role in ["Maintenance", "Logistik"]) and (volume_f1 < 0 or volume_fm2 < 0 or totalisator_out_assy_input < 0)
            err_prod = (role in ["Produksi", "Logistik"]) and (vol_rh_a < 0 or vol_lh_a < 0 or vol_rh_b < 0 or vol_lh_b < 0)
            
            if err_maint or err_prod:
                st.error("❌ Terdapat digit akhir yang lebih kecil dari digit awal! Periksa kembali inputan Anda.")
            elif conn is not None:
                try:
                    cur = conn.cursor()
                    cur.execute("""
                        SELECT total_pengisian, stok_akhir_level_meter, 
                               tank1_level, tank2_level, daily_tank_level, 
                               total_storage_level, totalisator_out_assy 
                        FROM daily_stock_log WHERE tanggal = %s AND id_area = 'KAP-1'
                    """, (tgl_input,))
                    ex_data = cur.fetchone()

                    ex_isi = ex_data[0] if ex_data and ex_data[0] is not None else 0.0
                    ex_stok = ex_data[1] if ex_data and ex_data[1] is not None else 0.0
                    ex_t1 = ex_data[2] if ex_data and ex_data[2] is not None else 0.0
                    ex_t2 = ex_data[3] if ex_data and ex_data[3] is not None else 0.0
                    ex_tdaily = ex_data[4] if ex_data and ex_data[4] is not None else 0.0
                    ex_tstorage = ex_data[5] if ex_data and ex_data[5] is not None else 0.0
                    ex_tot = ex_data[6] if ex_data and ex_data[6] is not None else 0.0

                    cur.execute("SELECT SUM(volume_keluar) FROM log_pengeluaran_dispenser WHERE tanggal = %s AND id_area = 'KAP-1' AND kategori_sap = 'GI Reguler'", (tgl_input,))
                    ex_reg_data = cur.fetchone()
                    ex_reguler = ex_reg_data[0] if ex_reg_data and ex_reg_data[0] is not None else 0.0

                    cur.execute("SELECT SUM(volume_keluar) FROM log_pengeluaran_dispenser WHERE tanggal = %s AND id_area = 'KAP-1' AND kategori_sap = 'GI Non-Reguler'", (tgl_input,))
                    ex_f5_data = cur.fetchone()
                    ex_f5 = ex_f5_data[0] if ex_f5_data and ex_f5_data[0] is not None else 0.0

                    is_maint = role in ["Maintenance", "Logistik"]
                    is_prod = role in ["Produksi", "Logistik"]

                    final_isi = volume_f1 if is_maint else ex_isi
                    final_stok = total_storage if is_maint else ex_stok
                    final_t1 = val_tank1 if is_maint else ex_t1
                    final_t2 = val_tank2 if is_maint else ex_t2
                    final_tdaily = daily_tank_actual if is_maint else ex_tdaily
                    final_tstorage = total_storage if is_maint else ex_tstorage
                    final_tot = totalisator_out_assy_input if is_maint else ex_tot

                    final_reguler = total_volume_reguler if is_prod else ex_reguler
                    final_f5 = volume_f5 if is_maint else ex_f5
                    final_pakai = final_reguler + final_f5

                    if is_maint:
                        if final_isi > 0:
                            cur.execute("""INSERT INTO log_penerimaan_tangki (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                                           VALUES (%s, %s, %s, %s, %s, %s)""",
                                        (tgl_input, 'KAP-1', 'GR', float(f1_awal), float(f1_akhir), float(final_isi)))
                        if volume_fm2 > 0:
                            cur.execute("""INSERT INTO log_transfer_internal (tanggal, id_area, fm2_awal, fm2_akhir, volume_transfer)
                                           VALUES (%s, %s, %s, %s, %s)""",
                                        (tgl_input, 'KAP-1', float(fm2_awal), float(fm2_akhir), float(volume_fm2)))
                        if volume_f5 > 0:
                            cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                        (tgl_input, 'KAP-1', 'GI Non-Reguler', 'F5', 0.0, 0.0, float(final_f5)))

                    if is_prod:
                        data_dispenser = [
                            ('RH (Shift A)', rh_a_awal, rh_a_akhir, vol_rh_a),
                            ('LH (Shift A)', lh_a_awal, lh_a_akhir, vol_lh_a),
                            ('RH (Shift B)', rh_b_awal, rh_b_akhir, vol_rh_b),
                            ('LH (Shift B)', lh_b_awal, lh_b_akhir, vol_lh_b)
                        ]
                        for n_pompa, aw, ak, vol in data_dispenser:
                            if vol > 0:
                                cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                            (tgl_input, 'KAP-1', 'GI Reguler', n_pompa, float(aw), float(ak), float(vol)))

                    stok_awal_val_k1 = get_stok_awal(conn, 'KAP-1', tgl_input)
                    stok_awal_aktual = float(stok_awal_val_k1) if stok_awal_val_k1 is not None else 0.0
                    loss = round((stok_awal_aktual + final_isi - final_pakai) - final_stok, 2)
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
                                float(round(stok_awal_aktual, 2)), float(round(final_isi, 2)),
                                float(round(final_pakai, 2)), float(round(final_stok, 2)),
                                float(round(loss, 2)), status_loss,
                                float(final_t1), float(final_t2), float(final_tdaily), float(final_tstorage), float(final_tot)
                                ))
                    
                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-1 tanggal {tgl_input.strftime('%d %B %Y')} berhasil diperbarui oleh {role.upper()}!")
                    st.toast("✅ Data berhasil digabungkan & disimpan ke sistem!", icon="💾")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database: {e}")
            else:
                st.error("Koneksi database terputus.")