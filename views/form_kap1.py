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
    # 1. Pastikan stok awal langsung menjadi float
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
                        tank1_input = st.number_input("Tanki 1 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tank2_input = st.number_input("Tanki 2 (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        daily_tank_input = st.number_input("Daily Tank (PV)", min_value=0.0, format="%.0f", step=1.0, value=None)
                        
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
                        f5_total_in = st.number_input("Flowmeter Liter RnD (F5)", min_value=0.0, format="%.0f", key="kap1_f5", step=1.0, value=None)
                        volume_f5 = float(f5_total_in) if f5_total_in is not None else 0.0
                with col_tot:
                    with st.container(border=True):
                        tot_out_awal_in = st.number_input("Flowmeter Out Awal", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tot_out_akhir_in = st.number_input("Flowmeter Out Akhir", min_value=0.0, format="%.0f", step=1.0, value=None)
                        tot_out_awal = float(tot_out_awal_in) if tot_out_awal_in is not None else 0.0
                        tot_out_akhir = float(tot_out_akhir_in) if tot_out_akhir_in is not None else 0.0
                        totalisator_out_assy_input = tot_out_akhir - tot_out_awal
            else:
                st.warning("🔒 Area ini khusus untuk Tim Logistik & Maintenance.")

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
                            rh_a_awal = float(rh_a_awal_in) if rh_a_awal_in is not None else 0.0
                            rh_a_akhir = float(rh_a_akhir_in) if rh_a_akhir_in is not None else 0.0
                            vol_rh_a = (rh_a_akhir - rh_a_awal) if rh_a_akhir >= rh_a_awal else 0.0
                    with col_lh_a:
                        st.write("**Pompa LH**")
                        with st.container(border=True):
                            lh_a_awal_in = st.number_input("Digit Awal LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_awal", step=1.0, value=None)
                            lh_a_akhir_in = st.number_input("Digit Akhir LH(A)", min_value=0.0, format="%.0f", key="kap1_lh_a_akhir", step=1.0, value=None)
                            lh_a_awal = float(lh_a_awal_in) if lh_a_awal_in is not None else 0.0
                            lh_a_akhir = float(lh_a_akhir_in) if lh_a_akhir_in is not None else 0.0
                            vol_lh_a = (lh_a_akhir - lh_a_awal) if lh_a_akhir >= lh_a_awal else 0.0

                with tab_shift_b:
                    col_rh_b, col_lh_b = st.columns(2)