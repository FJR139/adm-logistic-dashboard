import streamlit as st

def render_portal():
    # --- CSS Kustom untuk Portal ---
    st.markdown("""
        <style>
            .portal-card {
                background-color: white;
                border-radius: 12px;
                padding: 25px;
                border: 1px solid #E5E7EB;
                box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                height: 100%;
            }
            .portal-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.08);
                border-color: #E3000F;
            }
            .facility-list {
                color: #475569;
                font-size: 14px;
                line-height: 1.8;
                margin-bottom: 25px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("<h2 style='text-align: center; color: #1E293B; font-weight: 800;'>Selamat Datang di Portal Monitoring Stok</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size: 16px;'>Pilih Area Operasional untuk menginput data harian atau memantau status tangki secara <i>real-time</i>.</p>", unsafe_allow_html=True)
    st.write("---")
    st.write("")

    col1, spacer, col2 = st.columns([5, 1, 5])

    # ================= KARTU KAP 1 =================
    with col1:
        st.markdown("""
            <div class='portal-card'>
                <h3 style='margin-top: 0; color: #005A9E;'>🏭 Area KAP 1</h3>
                <div class='facility-list'>
                    ⛽ <b>Fuel Slow Station</b><br>
                    🛢️ Fuel Daily Tank<br>
                    ⏱️ Dispenser Meter
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        btn1_a, btn1_b = st.columns(2)
        with btn1_a:
            if st.button("📝 Form Input", use_container_width=True, type="primary", key="btn_in_k1"):
                st.session_state.selected_menu = "Form Input KAP 1"
                st.rerun()
        with btn1_b:
            if st.button("📊 Lihat Dashboard", use_container_width=True, type="secondary", key="btn_dash_k1"):
                st.session_state.selected_menu = "Dashboard Monitoring"
                st.rerun()

    # ================= KARTU KAP 2 =================
    with col2:
        st.markdown("""
            <div class='portal-card'>
                <h3 style='margin-top: 0; color: #005A9E;'>🏭 Area KAP 2</h3>
                <div class='facility-list'>
                    ⛽ <b>Fuel Slow Station</b><br>
                    🛢️ Fuel Daily Tank<br>
                    ⏱️ Dispenser Meter
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        btn2_a, btn2_b = st.columns(2)
        with btn2_a:
            if st.button("📝 Form Input", use_container_width=True, type="primary", key="btn_in_k2"):
                st.session_state.selected_menu = "Form Input KAP 2"
                st.rerun()
        with btn2_b:
            if st.button("📊 Lihat Dashboard", use_container_width=True, type="secondary", key="btn_dash_k2"):
                st.session_state.selected_menu = "Dashboard Monitoring"
                st.rerun()