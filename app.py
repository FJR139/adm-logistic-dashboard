import streamlit as st
import psycopg2
import datetime
import base64
import os

# Panggil modul tampilan
from views.portal import render_portal
from views.form_kap1 import render_kap1
from views.form_kap2 import render_kap2
from views.dashboard_bbm import render_dashboard
from views.dashboard_tren import render_dashboard_tren
from views.import_data import render_import_data

st.set_page_config(page_title="Sistem Monitoring BBM PT ADM", layout="wide", initial_sidebar_state="expanded")

# Inisialisasi Session State
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = "Portal Utama"

@st.cache_resource
def init_connection():
    try:
        db_url = st.secrets["SUPABASE_URL"]
        return psycopg2.connect(db_url)
    except Exception as e:
        st.error(f"Gagal terhubung ke database: {e}")
        return None

conn = init_connection()

st.markdown("""
    <style>
        /* ===== IMPORT GOOGLE FONTS: OPEN SANS ===== */
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

        /* Terapkan Open Sans ke elemen teks aplikasi secara terarah */
        .stMarkdown, .stTextInput, .stSelectbox, .stNumberInput, 
        .stButton > button, .stRadio, .stCheckbox, .stCaption,
        .stTabs, p, h1, h2, h3, h4, h5, h6, a, label {
            font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* PERLINDUNGAN: Jangan pernah timpa font ikon Streamlit */
        [data-testid="stIconMaterial"], 
        [data-testid="collapsedControl"],
        [data-testid="collapsedControl"] *,
        .material-symbols-rounded,
        .material-symbols-outlined,
        [data-testid="stSidebarCollapseButton"] * {
            font-family: "Material Symbols Rounded", "Source Sans Pro", sans-serif !important;
        }

        /* Sembunyikan elemen bawaan Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* 1. STYLING SIDEBAR (MENU NAVIGASI KIRI) */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 1px solid #E0E0E0;
        }
        
        .stSelectbox label {
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #333 !important;
            margin-bottom: 5px;
        }
        
        /* 2. STYLING HEADER ATAS */
        .adm-header { 
            background: linear-gradient(to right, #ffffff, #f4f6f9);
            padding: 20px 30px; 
            border-radius: 12px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.03); 
            margin-bottom: 30px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            border-left: 6px solid #E3000F;
            border-bottom: 1px solid #eee;
        }
        .adm-title { 
            margin: 0; 
            color: #005A9E; 
            font-family: 'Segoe UI', Roboto, sans-serif; 
            font-weight: 800; 
            font-size: 26px;
            letter-spacing: -0.5px;
        }
        
        /* 3. CSS UNTUK MEMPERBESAR TANGGAL */
        .stDateInput > label > div > p {
            font-size: 16px !important; 
            font-weight: bold !important;
            color: #005A9E !important; 
        }
        .stDateInput > div { font-size: 16px !important; }
        .stDateInput > div > div > div > input {
            font-size: 16px !important;
            padding: 8px 12px !important;
            font-weight: bold !important;
        }

        /* 4. TOMBOL UTAMA BERTEMA MERAH ADM */
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

        /* 5. TABS STYLING MODERN */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px 6px 0 0;
            padding: 8px 16px;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

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

# --- SIDEBAR NAVIGASI MENU ---
st.sidebar.markdown("<h3 style='color: #005A9E; font-weight: 800;'>MENU UTAMA</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

menu_options = ["Portal Utama", "Form Input KAP 1", "Form Input KAP 2", "Dashboard Monitoring", "Analisis Tren Bulanan", "Import Data Historis"]
menu = st.sidebar.radio("Navigasi", menu_options, index=menu_options.index(st.session_state.selected_menu), label_visibility="collapsed")
st.session_state.selected_menu = menu

st.sidebar.markdown("---")
st.sidebar.caption("© 2026 PT Astra Daihatsu Motor")

# --- ROUTING HALAMAN ---
if menu == "Portal Utama":
    render_portal()
elif menu == "Form Input KAP 1":
    render_kap1(conn)
elif menu == "Form Input KAP 2":
    render_kap2(conn)
elif menu == "Dashboard Monitoring":
    render_dashboard(conn)
elif menu == "Analisis Tren Bulanan":
    render_dashboard_tren(conn)
elif menu == "Import Data Historis":
    render_import_data(conn)