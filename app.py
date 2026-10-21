import streamlit as st
import psycopg2
from views.portal import render_portal
from views.form_kap1 import render_kap1
from views.form_kap2 import render_kap2
from views.dashboard_bbm import render_dashboard
from views.dashboard_tren import render_dashboard_tren
from views.import_data import render_import_data

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Logistik BBM ADM",
    page_icon="⛽",
    layout="wide"
)

# --- KONEKSI DATABASE SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        return psycopg2.connect(st.secrets["database_url"])
    except Exception as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None

conn = init_connection()

# --- INISIALISASI SESSION STATE ---
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Portal Utama"

# ==========================================
# SIDEBAR: KONTROL LOGIN & NAVIGASI ROLE
# ==========================================
st.sidebar.markdown("## 🔐 Autorisasi & Akses")
selected_role = st.sidebar.selectbox(
    "Pilih Departemen / Role",
    ["Logistik", "Maintenance", "Produksi"],
    help="Pilih peran Anda untuk menyesuaikan hak akses menu dan form input."
)

# Simpan role ke session state
st.session_state.role = selected_role
role = st.session_state.role

st.sidebar.write("---")
st.sidebar.markdown("### 📌 Navigasi Menu")

# Pembatasan Menu (RBAC Sidebar Menu)
if role == "Maintenance":
    # Menghapus "Portal Utama", hanya menyisakan form
    menu_options = ["Form Input KAP 1", "Form Input KAP 2"]
    st.sidebar.info("🛠️ **Maintenance Mode:** Akses terbatas pada input Tangki & Penerimaan.")
elif role == "Produksi":
    # Menghapus "Portal Utama", hanya menyisakan form
    menu_options = ["Form Input KAP 1", "Form Input KAP 2"]
    st.sidebar.info("⚙️ **Produksi Mode:** Akses terbatas pada Dispenser & Totalisator.")
else:  # Logistik (Superadmin / Validator)
    # Logistik tetap memiliki akses penuh ke semua halaman
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
    st.session_state.selected_menu = menu_options[0]

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