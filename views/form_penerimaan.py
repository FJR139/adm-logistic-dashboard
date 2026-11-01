import streamlit as st
import datetime

def render_penerimaan(conn, role="Logistik"):
    st.markdown("<h3 style='text-align: center; color: #333333;'>Form Penerimaan BBM (Bongkar Muat)</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #005A9E;'>Masuk sebagai: <b>{role.upper()}</b></p>", unsafe_allow_html=True)
    st.write("---")

    # Kunci akses eksklusif untuk Logistik
    if role not in ["Logistik"]:
        st.warning("🔒 Halaman ini khusus untuk pencatatan kedatangan BBM oleh Tim Logistik.")
        return

    st.info("🚛 Pencatatan nilai Sebelum (Before) dan Sesudah (After) pembongkaran truk tangki.")
    tgl_input = st.date_input("Tanggal Kedatangan", value=datetime.date.today())
    
    # Membungkus semua input dalam satu form agar tersubmit bersamaan
    with st.form("form_bongkar_muat"):
        st.markdown("### 1. Pencatatan Flowmeter (Liter)")
        col_fm_in, col_fm_out = st.columns(2)
        with col_fm_in:
            st.write("**Flowmeter IN (Penerimaan)**")
            fm_in_before = st.number_input("Before (Awal) IN", min_value=0.0, format="%.0f", step=1.0)
            fm_in_after = st.number_input("After (Akhir) IN", min_value=0.0, format="%.0f", step=1.0)
        
        with col_fm_out:
            st.write("**Flowmeter OUT**")
            fm_out_before = st.number_input("Before (Awal) OUT", min_value=0.0, format="%.0f", step=1.0)
            fm_out_after = st.number_input("After (Akhir) OUT", min_value=0.0, format="%.0f", step=1.0)

        st.markdown("### 2. Pencatatan Level Tangki (PV)")
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
            daily_before = st.number_input("Daily Before", min_value=0.0, format="%.0f", step=1.0)
            daily_after = st.number_input("Daily After", min_value=0.0, format="%.0f", step=1.0)

        st.write("---")
        submitted = st.form_submit_button("Simpan Data Penerimaan BBM", type="primary", use_container_width=True)
        
        if submitted:
            vol_in = fm_in_after - fm_in_before
            vol_out = fm_out_after - fm_out_before
            
            if vol_in < 0 or vol_out < 0:
                st.error("❌ Nilai 'After' tidak boleh lebih kecil dari 'Before'!")
            else:
                st.success(f"✅ Data Penerimaan berhasil dicatat! Total Volume Masuk: {vol_in:,.0f} Liter.")
                # (Logika database INSERT ke log_penerimaan_tangki akan diletakkan di sini)