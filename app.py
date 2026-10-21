import streamlit as st
import psycopg2
import base64
import os
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

# --- FUNGSI LOAD GAMBAR BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "daihatsu.png")
logo_b64 = get_base64_image(LOGO_PATH)

if logo_b64:
    img_tag = f'<img src="data:image/png;base64,{logo_b64}" height="55" style="margin-right: 20px; object-fit: contain;">'
else:
    img_tag = f'<div style="font-size: 24px; font-weight: 900; color: #E3000F; margin-right: 20px;">ADM</div>'

# --- CSS GLOBAL & HEADER STYLING ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        .stMarkdown, .stTextInput, .stSelectbox, .stNumberInput, 
        .stButton > button, .stRadio, .stCheckbox, .stCaption,
        .stTabs, p, h1, h2, h3, h4, h5, h6, a, label {
            font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        [data-testid="stIconMaterial"], 
        [data-testid="collapsedControl"],
        [data-testid="collapsedControl"] *,
        .material-symbols-rounded,
        .material-symbols-outlined,
        [data-testid="stSidebarCollapseButton"] * {
            font-family: "Material Symbols Rounded", "Source Sans Pro", sans-serif !important;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        .adm-header { 
            background: linear-gradient(to right, #ffffff, #f4f6f9);
            padding: 16px 25px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.03); 
            margin-bottom: 25px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            border-left: 6px solid #E3000F;
            border-bottom: 1px solid #eee;
        }
        .adm-title { 
            margin: 0; 
            color: #005A9E; 
            font-family: 'Open Sans', 'Segoe UI', Roboto, sans-serif; 
            font-weight: 800; 
            font-size: 24px;
            letter-spacing: -0.5px;
        }
        
        div.stButton > button[kind="primary"] {
            background-color: #E3000F !important;
            border-color: #E3000F !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 10px rgba(227, 0, 15, 0.2) !important;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #B5000C !important;
            border-color: #B5000C !important;
            box-shadow: 0 6px 14px rgba(227, 0, 15, 0.35) !important;
            transform: translateY(-2px);
        }
    </style>
""", unsafe_allow_html=True)

# --- RENDER HEADER UTAMA DENGAN LOGO ---
st.markdown(f"""
    <div class='adm-header'>
        <div style='display: flex; align-items: center;'>
            {img_tag}
            <div>
                <h3 class='adm-title'>Logistics Monitoring Dashboard</h3>
                <p style="margin: 3px 0 0 0; font-size: 13px; color: #555; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">PT Astra Daihatsu Motor</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

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