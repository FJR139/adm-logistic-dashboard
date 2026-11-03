import streamlit as st
import pandas as pd
import datetime
from utils import get_stok_awal

def render_kap2(conn, role="Logistik", mode=None):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Input Data Harian - KAP-2</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #005A9E;'>Masuk sebagai: <b>{role.upper()}</b></p>", unsafe_allow_html=True)
    st.write("---")

    col_date, spacer = st.columns([3, 5])
    with col_date:
        st.markdown("### 🗓️ Tanggal")
        tgl_input = st.date_input("Tanggal", value=datetime.date.today(), max_value=datetime.date.today(), label_visibility="collapsed")
    st.write("")

    stok_awal_kemarin_kap2 = get_stok_awal(conn, "KAP-2", tgl_input)
    stok_awal_display = stok_awal_kemarin_kap2 if stok_awal_kemarin_kap2 is not None else 0.0

    # --- INISIALISASI VARIABEL DEFAULT (PENTING AGAR DATABASE TIDAK ERROR) ---
    volume_f1_kap2 = 0.0; f1_awal_kap2 = 0.0; f1_akhir_kap2 = 0.0 
    pv_tank1_kap2 = 0.0; pv_tank2_kap2 = 0.0; pv_daily_kap2 = 0.0
    total_stok_akhir_kap2 = 0.0
    volume_keluar_kap2 = 0.0; analog_awal_kap2 = 0.0; analog_akhir_kap2 = 0.0

    # ================= STRUKTUR TAB DAILY INPUT =================
    if mode == "Daily":
        tab_logistik, tab_produksi = st.tabs(["🧑‍🔧 Tim Logistik", "⚙️ Tim Produksi"])
        
        # --- TAB MILIK LOGISTIK ---
        with tab_logistik:
            if role in ["Logistik", "Maintenance"]:
                st.markdown("### 1. Pencatatan Flowmeter OUT (Transfer BBM)")
                with st.container(border=True):
                    col_f1_awal, col_f1_akhir = st.columns(2)
                    with col_f1_awal:
                        f1_awal_in = st.number_input("Flowmeter Awal (Liter)", min_value=0.0, format="%.0f", key="kap2_f1_a", step=1.0, value=None)
                    with col_f1_akhir:
                        f1_akhir_in = st.number_input("Flowmeter Akhir (Liter)", min_value=0.0, format="%.0f", key="kap2_f1_b", step=1.0, value=None)
                    f1_awal_kap2 = f1_awal_in if f1_awal_in is not None else 0.0
                    f1_akhir_kap2 = f1_akhir_in if f1_akhir_in is not None else 0.0
                    volume_f1_kap2 = f1_akhir_kap2 - f1_awal_kap2

                st.markdown("### 2. Level Meter Tangki (Akhir Shift)")
                with st.container(border=True):
                    st.caption(f"ℹ️ Stok Awal (Level Akhir Kemarin): **{stok_awal_display:,.0f} Liter**")
                    col_t1, col_t2, col_dt = st.columns(3)
                    with col_t1:
                        pv_tank1_in = st.number_input("Tank 1 (PV)", min_value=0.0, format="%.0f", key="kap2_pv1", step=1.0, value=None)
                        pv_tank1_kap2 = pv_tank1_in if pv_tank1_in is not None else 0.0
                    with col_t2:
                        pv_tank2_in = st.number_input("Tank 2 (PV)", min_value=0.0, format="%.0f", key="kap2_pv2", step=1.0, value=None)
                        pv_tank2_kap2 = pv_tank2_in if pv_tank2_in is not None else 0.0
                    with col_dt:
                        pv_daily_in = st.number_input("Daily Tank (PV)", min_value=0.0, format="%.0f", key="kap2_pv_dt", step=1.0, value=None)
                        pv_daily_kap2 = pv_daily_in if pv_daily_in is not None else 0.0
                    
                    total_stok_akhir_kap2 = pv_tank1_kap2 + pv_tank2_kap2 + pv_daily_kap2
            else:
                st.warning("🔒 Area ini khusus untuk Tim Logistik & Maintenance.")

        # --- TAB MILIK PRODUKSI ---
        with tab_produksi:
            if role in ["Produksi", "Logistik"]:
                st.markdown("### 2. Dispenser Jalur Produksi")
                st.info("💡 KAP-2 beroperasi dalam 1 Shift Pagi.")
                with st.container(border=True):
                    col_rh, col_lh = st.columns(2)
                    with col_rh:
                        st.write("**Pompa RH**")
                        rh_awal_in = st.number_input("Digit Awal RH (Liter)", min_value=0.0, format="%.0f", key="kap2_rh_a", step=1.0, value=None)
                        rh_akhir_in = st.number_input("Digit Akhir RH (Liter)", min_value=0.0, format="%.0f", key="kap2_rh_b", step=1.0, value=None)
                        rh_awal = rh_awal_in if rh_awal_in is not None else 0.0
                        rh_akhir = rh_akhir_in if rh_akhir_in is not None else 0.0
                        vol_rh = (rh_akhir - rh_awal) if rh_akhir >= rh_awal else 0.0
                    with col_lh:
                        st.write("**Pompa LH**")
                        lh_awal_in = st.number_input("Digit Awal LH (Liter)", min_value=0.0, format="%.0f", key="kap2_lh_a", step=1.0, value=None)
                        lh_akhir_in = st.number_input("Digit Akhir LH (Liter)", min_value=0.0, format="%.0f", key="kap2_lh_b", step=1.0, value=None)
                        lh_awal = lh_awal_in if lh_awal_in is not None else 0.0
                        lh_akhir = lh_akhir_in if lh_akhir_in is not None else 0.0
                        vol_lh = (lh_akhir - lh_awal) if lh_akhir >= lh_awal else 0.0
                    
                    volume_keluar_kap2 = vol_rh + vol_lh
            else:
                st.warning("🔒 Area khusus Tim Produksi.")

    # ... (Biarkan logika validasi pre-submit seperti aslinya) ...

    # ================= STEP 3: DATABASE MERGING & SUBMIT =================
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b2:
        if st.button("SUBMIT DATA HARIAN KAP-2", use_container_width=True, type="primary", key="kap2_submit"):
            if (role in ["Maintenance", "Logistik"] and volume_f1_kap2 < 0) or \
               (role in ["Produksi", "Logistik"] and volume_keluar_kap2 < 0):
                st.error("❌ Digit akhir tidak boleh lebih kecil dari digit awal!")
            elif conn is not None:
                try:
                    cur = conn.cursor()

                    cur.execute("SELECT total_pengisian, total_pemakaian, stok_akhir_level_meter FROM daily_stock_log WHERE tanggal = %s AND id_area = 'KAP-2'", (tgl_input,))
                    existing_data = cur.fetchone()
                
                    ex_pengisian = float(existing_data[0]) if (existing_data and existing_data[0] is not None) else 0.0
                    ex_pemakaian = float(existing_data[1]) if (existing_data and existing_data[1] is not None) else 0.0
                    ex_stok_akhir = float(existing_data[2]) if (existing_data and existing_data[2] is not None) else 0.0

                    final_pengisian = ex_pengisian
                    final_pemakaian = float(volume_keluar_kap2) if role in ["Produksi", "Logistik"] else ex_pemakaian
                    # Ubah di bagian STEP 3: DATABASE MERGING & SUBMIT
                    final_stok_akhir = float(total_stok_akhir_kap2) if role in ["Maintenance", "Logistik"] else ex_stok_akhir

                    if role in ["Maintenance", "Logistik"] and final_pengisian > 0:
                        cur.execute("""INSERT INTO log_penerimaan_tangki (tanggal, id_area, kategori_sap, fm1_awal, fm1_akhir, volume_terima)
                                       VALUES (%s, %s, %s, %s, %s, %s)""",
                                    (tgl_input, 'KAP-2', 'GR', float(f1_awal_kap2), float(f1_akhir_kap2), float(final_pengisian)))

                    if role in ["Produksi", "Logistik"] and final_pemakaian > 0:
                        if vol_rh > 0:
                            cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                        (tgl_input, 'KAP-2', 'GI Reguler', 'POMPA_RH_PAGI', float(rh_awal), float(rh_akhir), float(vol_rh)))
                        if vol_lh > 0:
                            cur.execute("""INSERT INTO log_pengeluaran_dispenser (tanggal, id_area, kategori_sap, id_flowmeter, angka_meter_awal, angka_meter_akhir, volume_keluar)
                                           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                        (tgl_input, 'KAP-2', 'GI Reguler', 'POMPA_LH_PAGI', float(lh_awal), float(lh_akhir), float(vol_lh)))

                    stok_awal_val = get_stok_awal(conn, 'KAP-2', tgl_input)
                    stok_awal_aktual = float(stok_awal_val) if stok_awal_val is not None else 0.0
                    loss_kap2 = round((float(stok_awal_aktual) + float(final_pengisian) - float(final_pemakaian)) - float(final_stok_akhir), 2)
                    status_loss_kap2 = "SELISIH" if abs(loss_kap2) > 0.01 else "AMAN"

                    cur.execute("""INSERT INTO daily_stock_log
                                   (tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss)
                                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                   ON CONFLICT (tanggal, id_area) DO UPDATE SET
                                   stok_awal_level_meter = EXCLUDED.stok_awal_level_meter,
                                   total_pengisian = EXCLUDED.total_pengisian,
                                   total_pemakaian = EXCLUDED.total_pemakaian,
                                   stok_akhir_level_meter = EXCLUDED.stok_akhir_level_meter,
                                   loss_kalkulasi = EXCLUDED.loss_kalkulasi,
                                   status_loss = EXCLUDED.status_loss;""",
                                (tgl_input, 'KAP-2',
                                 float(round(stok_awal_aktual, 2)), float(round(final_pengisian, 2)),
                                 float(round(final_pemakaian, 2)), float(round(final_stok_akhir, 2)),
                                 float(round(loss_kap2, 2)), status_loss_kap2))

                    conn.commit()
                    cur.close()
                    st.success(f"✅ Data KAP-2 tanggal {tgl_input.strftime('%d %B %Y')} berhasil diperbarui oleh {role.upper()}!")
                    st.toast("✅ Data berhasil digabungkan & disimpan ke sistem!", icon="💾")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Terjadi kesalahan database: {e}")
            else:
                st.error("Koneksi database terputus.")