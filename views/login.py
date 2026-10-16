import streamlit as st
import pandas as pd
from utils.auth import verify_password

def render_login(conn):
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center; color: #005A9E;'>🔐 ADM Logistics Portal</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Silakan masuk dengan kredensial Anda</p>", unsafe_allow_html=True)
            st.write("---")

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Masuk", type="primary", use_container_width=True)

                if submit:
                    # 1. Cek apakah kolom diisi
                    if username and password:
                        try:
                            # 2. Cari user di database
                            query = "SELECT password_hash, role FROM users WHERE username = %s"
                            df_user = pd.read_sql(query, conn, params=(username,))

                            if not df_user.empty:
                                hashed_pw = df_user.iloc[0]['password_hash']
                                role = df_user.iloc[0]['role']
                                if verify_password(password, hashed_pw):
                                    st.success("Login berhasil Memuat Sistem...")
                                    st.session_state.logged_in = True
                                    st.session_state.username = username
                                    st.session_state.user_role = role
                                    st.rerun()
                                else:
                                    st.error("❌Password Salah")
                            else:
                                st.error("❌Username tidak ditemukan")
                        except Exception as e:
                            st.error(f"Terjadi kesalahan koneksi: {e}")
                    else:
                        st.warning("⚠️Harap isi username dan password!")