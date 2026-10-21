import streamlit as st
import psycopg2
import datetime
import base64
import os

# Mengatur konfigurasi halaman (HARUS PALING ATAS)
st.set_page_config(page_title="Sistem Monitoring BBM PT ADM", layout="wide", initial_sidebar_state="expanded")

# --- 1. IMPORT MODUL TAMPILAN ---
from views.login import render_login
from views.portal import render_portal
from views.form_kap1 import render_kap1
from views.form_kap2 import render_kap2
from views.dashboard_bbm import render_dashboard
from views.dashboard_tren import render_dashboard_tren
from views.import_data import render_import_data

st.set_page_config(
    page_title="Dashboard Logistik BBM ADM",
    page_icon="⛽",
    layout="wide"
)

# --- 2. KONEKSI DATABASE ---
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["database_url"])
    except Exception as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None

# Definisi 'conn' di awal agar bisa digunakan oleh modul di bawahnya
conn = init_connection()

# --- 3. INISIALISASI SESSION STATE (MODE DEVELOPER) ---
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Portal Utama"

st.sidebar.markdown("## 🔐 Autorisasi & Akses")
selected_role = st.sidebar.selectbox(
    "Pilih Departemen / Role",
    ["Logistik", "Maintenance", "Produksi"],
    help="Pilih peran Anda untuk menyesuaikan hak akses menu dan form input"
)

st.session_state.role = selected_role
role = st.session_state.role

st.sidebar.write("---")
st.sidebar.markdown("### 📌 Navigasi Menu")

if role == "Maintenance":
    menu_options = ["Portal Utama", "Form Input KAP 1", "Form Input KAP 2"]
    st.sidebar.info("🛠️ **Maintenance Mode:** Akses terbatas pada input Tangki & Penerimaan.")
elif role == "Produksi":
    menu_options = ["Portal Utama", "Form Input KAP 1", "Form Input KAP 2"]
    st.sidebar.info("⚙️ **Produksi Mode:** Akses terbatas pada Dispenser & Totalisator.")
else:  # Logistik (Superadmin / Validator)
    menu_options = [
        "Portal Utama", 
        "Form Input KAP 1", 
        "Form Input KAP 2", 
        "Dashboard Monitoring", 
        "Dashboard Analisis Tren", 
        "Import Data Historis"
    ]
    st.sidebar.success("👑 **Logistik Mode:** Akses penuh (Superadmin & Validator).")

# Sinkronisasi pilihan menu di sidebar dengan session state
if st.session_state.selected_menu not in menu_options:
    st.session_state.selected_menu = "Portal Utama"

selected_menu = st.sidebar.radio(
    "Pilih Menu", 
    menu_options, 
    index=menu_options.index(st.session_state.selected_menu)
)
st.session_state.selected_menu = selected_menu

st.sidebar.write("---")
st.sidebar.caption("PT Astra Daihatsu Motor (ADM) © 2026")

# ==========================================
# ROUTING HALAMAN UTAMA
# ==========================================
if conn:
    if selected_menu == "Portal Utama":
        render_portal()
    elif selected_menu == "Form Input KAP 1":
        render_kap1(conn, role=role)  # Mengirim parameter role ke form KAP-1
    elif selected_menu == "Form Input KAP 2":
        render_kap2(conn, role=role)  # Mengirim parameter role ke form KAP-2
    elif selected_menu == "Dashboard Monitoring":
        render_dashboard(conn)
    elif selected_menu == "Dashboard Analisis Tren":
        render_dashboard_tren(conn)
    elif selected_menu == "Import Data Historis":
        render_import_data(conn)
else:
    st.error("❌ Koneksi ke database belum siap. Periksa konfigurasi secrets Anda.")