import streamlit as st
import datetime
from utils import get_stok_awal

@st.dialog("⚠️ Konfirmasi Submit Data")
def confirm_submit_dialog(trigger_key):
    st.write("Apakah Anda yakin seluruh data angka meteran dan tangki yang diinput sudah benar?")
    st.info("Data yang disubmit akan langsung mengubah laporan Dasbor Utama dan direkam untuk audit.")
    
    col_batal, col_yakin = st.columns(2)
    with col_batal:
        if st.button("Tinjau Ulang", use_container_width=True, key=f"cancel_{trigger_key}"):
            st.rerun() # Tutup dialog
    with col_yakin:
        if st.button("Ya, Submit Data", type="primary", use_container_width=True, key=f"ok_{trigger_key}"):
            st.session_state[trigger_key] = True
            st.rerun()

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
    stok_awal_display = float(stok_awal_kemarin) if stok_awal_kemarin is not None else 0.0

    # --- INISIALISASI VARIABEL DEFAULT ---
    val_tank1 = 0.0; val_tank2 = 0.0; val_daily = 0.0; daily_tank_actual = 0.0; total_storage = 0.0
    vol_rh_a = 0.0; rh_a_awal = 0.0; rh_a_akhir = 0.0
    vol_lh_a = 0.0; lh_a_awal = 0.0; lh_a_akhir = 0.0
    vol_rh_b = 0.0; rh_b_awal = 0.0; rh_b_akhir = 0.0
    vol_lh_b = 0.0; lh_b_awal = 0.0; lh_b_akhir = 0.0
    volume_f5 = 0.0; total_volume_reguler = 0.0
    totalisator_out_assy_input = 0.0; tot_out_awal = 0.0; tot_out_akhir = 0.0

    # ================= STRUKTUR TAB DAILY INPUT =================
    if mode == "Daily":
        tab_logistik, tab_produksi = st.tabs(["🧑‍🔧 Tim Logistik", "⚙️ Tim Produksi"])
        
        # --- TAB MILIK LOGISTIK ---
        with tab_logistik:
            if role in ["Logistik", "Maintenance"]:
                st.markdown("### 1. Level Meter Tangki (Awal Shift)")
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    with st.container(border=True):
                        tank1_input = st.number_input("Tanki 1 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None, key="kap1_pv1")
                        tank2_input = st.number_input("Tanki 2 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None, key="kap1_pv2")
                        daily_tank_input = st.number_input("Daily Tank (PV)", min_value=0.0, format="%.0f", step=1.0, value=None, key="kap1_pv_dt")
                        
                        val_tank1 = float(tank1_input) if tank1_input is not None else 0.0
                        val_tank2 = float(tank2_input) if tank2_input is not None else 0.0
                        val_daily = float(daily_tank_input) if daily_tank_input is not None else 0.0
                        daily_tank_actual = val_daily * 2
                        total_storage = val_tank1 + val_tank2 + daily_tank_actual
                with col_t2:
                    st.info(f"💡 Info: Nilai Daily Tank otomatis dikali 2\n\n**Total Storage:** {total_storage:,.0f} Liter")

                st.markdown("### 2. Dispenser Non-Reguler (R&D) & Flowmeter")
                col_f5, col_tot = st.columns(2)
                with col_f5:
                    with st.container(border=True):
                        st.write("**Flowmeter RnD (F5)**")
                        f5_awal_in = st.number_input("Meter Awal RnD", min_value=0.0, format="%.0f", key="kap1_f5_awal", step=1.0, value=None)
                        f5_akhir_in = st.number_input("Meter Akhir RnD", min_value=0.0, format="%.0f", key="kap1_f5_akhir", step=1.0, value=None)
        
                        f5_awal = float(f5_awal_in) if f5_awal_in is not None else 0.0
                        f5_akhir = float(f5_akhir_in) if f5_akhir_in is not None else 0.0
                        # Sistem menghitung otomatis pemakaian harian
                        volume_f5 = (f5_akhir - f5_awal) if f5_akhir >= f5_awal else 0.0
            else:
                st.warning("🔒 Area ini khusus untuk Tim Logistik & Maintenance.")

        # --- TAB MILIK PRODUKSI ---
        with tab_produksi:
            if role in ["Produksi", "Logistik"]:
                st.markdown("### 3. Dispenser Jalur Produksi")
                
                # BUG FIX: Mengganti Tab bersarang (nested tabs) menjadi sub-judul biasa
                st.markdown("#### ⚙️ SHIFT A")
                with st.container(border=True):
                    col_rh_a, col_lh_a = st.columns(2)
                    with col_rh_a:
                        st.write("**Pompa RH (A)**")
                        rh_a_awal_in = st.number_input("Digit Awal RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_awal", step=1.0, value=None)
                        rh_a_akhir_in = st.number_input("Digit Akhir RH(A)", min_value=0.0, format="%.0f", key="kap1_rh_a_akhir", step=1.0, value=None)        
                        rh_a_awal = float(rh_a_awal_in) if rh_a_awal_in is not None else 0.0
                        rh_a_akhir = float(rh_a_akhir_in) if rh_a_akhir_in is not None else 0.0
                        vol_rh_a = (rh_a_akhir - rh_a_awal) if rh_a_akhir >= rh_a_awal else 0.0
                    with col_lh_a:
                        st.write("**Pompa LH (A)**")
                        lh_a_awal_in = st.number_input("Digit Awal LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_awal", step=1.0, value=None)
                        lh_a_akhir_in = st.number_input("Digit Akhir LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_akhir", step=1.0, value=None)
                        lh_a_awal = float(lh_a_awal_in) if lh_a_awal_in is not None else 0.0
                        lh_a_akhir = float(lh_a_akhir_in) if lh_a_akhir_in is not None else 0.0
                        vol_lh_a = (lh_a_akhir - lh_a_awal) if lh_a_akhir >= lh_a_awal else 0.0

                st.markdown("#### ⚙️ SHIFT B")
                with st.container(border=True):
                    col_rh_b, col_lh_b = st.columns(2)
                    with col_rh_b:
                        st.write("**Pompa RH (B)**")
                        rh_b_awal_in = st.number_input("Digit Awal RH(B)", min_value=0.0, format="%.0f", key="kap1_rh_b_awal", step=1.0, value=None)
                        rh_b_akhir_in = st.number_input("Digit Akhir RH(B)", min_value=0.0, format="%.0f", key="kap1_rh_b_akhir", step=1.0, value=None)
                        rh_b_awal = float(rh_b_awal_in) if rh_b_awal_in is not None else 0.0
                        rh_b_akhir = float(rh_b_akhir_in) if rh_b_akhir_in is not None else 0.0
                        vol_rh_b = (rh_b_akhir - rh_b_awal) if rh_b_akhir >= rh_b_awal else 0.0
                    with col_lh_b:
                        st.write("**Pompa LH (B)**")
                        lh_b_awal_in = st.number_input("Digit Awal LH(B)", min_value=0.0, format="%.0f", key="kap1_lh_b_awal", step=1.0, value=None)
                        lh_b_akhir_in = st.number_input("Digit Akhir LH(B)", min_value=0.0, format="%.0f", key="kap1_lh_b_akhir", step=1.0, value=None)
                        lh_b_awal = float(lh_b_awal_in) if lh_b_awal_in is not None else 0.0
                        lh_b_akhir = float(lh_b_akhir_in) if lh_b_akhir_in is not None else 0.0
                        vol_lh_b = (lh_b_akhir - lh_b_awal) if lh_b_akhir >= lh_b_awal else 0.0

                total_volume_reguler = vol_rh_a + vol_lh_a + vol_rh_b + vol_lh_b
            else:
                st.warning("🔒 Area khusus Tim Produksi.")

    # ================= PRE-SUBMIT LIVE VALIDATION =================
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

    total_form_pemakaian_preview = totalisator_out_assy_input + volume_f5 + total_volume_reguler
    sim_pakai = total_form_pemakaian_preview if total_form_pemakaian_preview > 0 else ex_pakai_prev
    sim_stok = total_storage if total_storage > 0 else ex_stok_prev
    
    if sim_stok > 0 or sim_pakai > 0:
        est_loss = round((stok_awal_display + ex_isi_prev - sim_pakai) - sim_stok, 2)
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
        # Inisialisasi state unik untuk dialog KAP-1
        trigger_key = "confirm_submit_kap1"
        if trigger_key not in st.session_state:
            st.session_state[trigger_key] = False

        # Tombol utama memanggil pop-up dialog (dengan validasi awal)
        if st.button("SUBMIT DATA HARIAN KAP-1", use_container_width=True, type="primary", key="kap1_submit_btn"):
            err_maint_pre = (role in ["Maintenance", "Logistik"]) and (totalisator_out_assy_input < 0 or volume_f5 < 0)
            err_prod_pre = (role in ["Produksi", "Logistik"]) and (vol_rh_a < 0 or vol_lh_a < 0 or vol_rh_b < 0 or vol_lh_b < 0)
            if err_maint_pre or err_prod_pre:
                st.error("❌ Terdapat digit akhir yang lebih kecil dari digit awal! Periksa kembali inputan Anda.")
            else:
                confirm_submit_dialog(trigger_key)

        # Kueri database HANYA berjalan jika operator menekan "Ya, Submit Data" di dalam pop-up
        if st.session_state[trigger_key]:
            st.session_state[trigger_key] = False  # Reset state setelah dieksekusi
            
            err_maint = (role in ["Maintenance", "Logistik"]) and (totalisator_out_assy_input < 0 or volume_f5 < 0)
            err_prod = (role in ["Produksi", "Logistik"]) and (vol_rh_a < 0 or vol_lh_a < 0 or vol_rh_b < 0 or vol_lh_b < 0)
            
            if err_maint or err_prod:
                st.error("❌ Terdapat digit akhir yang lebih kecil dari digit awal! Periksa kembali inputan Anda.")
            elif conn is not None:
                try:
                    cur = conn.cursor()
                    
                    # MULAI BLOK KUERI DATABASE YANG SEBELUMNYA HILANG
                    cur.execute("SELECT total_pengisian, total_pemakaian, stok_akhir_level_meter, tank1_level, tank2_level, daily_tank_level, total_storage_level, totalisator_out_assy FROM daily_stock_log WHERE tanggal = %s AND id_area = 'KAP-1'", (tgl_input,))
                    existing_data = cur.fetchone()

                    ex_pengisian = float(existing_data[0]) if (existing_data and existing_data[0] is not None) else 0.0
                    ex_pemakaian = float(existing_data[1]) if (existing_data and existing_data[1] is not None) else 0.0
                    ex_stok_akhir = float(existing_data[2]) if (existing_data and existing_data[2] is not None) else 0.0
                    ex_t1 = float(existing_data[3]) if (existing_data and existing_data[3] is not None) else 0.0
                    ex_t2 = float(existing_data[4]) if (existing_data and existing_data[4] is not None) else 0.0
                    ex_tdaily = float(existing_data[5]) if (existing_data and existing_data[5] is not None) else 0.0
                    ex_tstorage = float(existing_data[6]) if (existing_data and existing_data[6] is not None) else 0.0
                    ex_tot = float(existing_data[7]) if (existing_data and existing_data[7] is not None) else 0.0

                    is_maint = role in ["Maintenance", "Logistik"]
                    is_prod = role in ["Produksi", "Logistik"]

                    final_pengisian = ex_pengisian
                    
                    total_pemakaian_form = float(totalisator_out_assy_input) + float(volume_f5) + float(total_volume_reguler)
                    final_pemakaian = total_pemakaian_form if total_pemakaian_form > 0 else ex_pemakaian
                    
                    final_stok_akhir = float(total_storage) if is_maint else ex_stok_akhir
                    
                    final_t1 = float(val_tank1) if is_maint else ex_t1
                    final_t2 = float(val_tank2) if is_maint else ex_t2
                    final_tdaily = float(daily_tank_actual) if is_maint else ex_tdaily
                    final_tstorage = float(total_storage) if is_maint else ex_tstorage
                    final_tot = float(totalisator_out_assy_input) if is_maint else ex_tot

                    if is_maint and totalisator_out_assy_input > 0:
                         cur.execute("DELETE FROM log_pengeluaran_dispenser WHERE tanggal = %s AND id_area = 'KAP-1' AND id_flowmeter IN ('FLOWMETER_OUT', 'F5_RnD')", (tgl_input,))
                         cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-1', 'GI Reguler', 'FLOWMETER_OUT', float(tot_out_awal), float(tot_out_akhir), float(totalisator_out_assy_input)))
                    
                    if is_maint and volume_f5 > 0:
                        cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-1', 'GI Non-Reguler', 'F5_RnD', 0.0, 0.0, float(volume_f5)))

                    if is_prod and total_volume_reguler > 0:
                        cur.execute("DELETE FROM log_pengeluaran_dispenser WHERE tanggal = %s AND id_area = 'KAP-1' AND id_flowmeter LIKE 'POMPA%%'", (tgl_input,))
                        data_dispenser = [
                            ('POMPA_RH_SHIFTA', rh_a_awal, rh_a_akhir, vol_rh_a),
                            ('POMPA_LH_SHIFTA', lh_a_awal, lh_a_akhir, vol_lh_a),
                            ('POMPA_RH_SHIFTB', rh_b_awal, rh_b_akhir, vol_rh_b),
                            ('POMPA_LH_SHIFTB', lh_b_awal, lh_b_akhir, vol_lh_b)
                        ]
                        for n_pompa, aw, ak, vol in data_dispenser:
                            if vol > 0:
                                cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                            (tgl_input, 'KAP-1', 'GI Reguler', n_pompa, float(aw), float(ak), float(vol)))

                    loss = round((stok_awal_display + final_pengisian - final_pemakaian) - final_stok_akhir, 2)
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
                                float(round(stok_awal_display, 2)), float(round(final_pengisian, 2)),
                                float(round(final_pemakaian, 2)), float(round(final_stok_akhir, 2)),
                                float(round(loss, 2)), status_loss,
                                float(final_t1), float(final_t2), float(final_tdaily), float(final_tstorage), float(final_tot)
                                ))
                    # AKHIR BLOK KUERI DATABASE
                    
                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-1 tanggal {tgl_input.strftime('%d %B %Y')} berhasil diperbarui oleh {role.upper()}!")
                    st.toast("✅ Data berhasil digabungkan & disimpan ke sistem!", icon="💾")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database saat eksekusi Query: {e}")
            else:
                st.error("Koneksi database terputus.")