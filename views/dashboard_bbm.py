import streamlit as st
import pandas as pd
import datetime
import base64

def get_image_as_base64(file_path):
    try:
        with open(file_path, "rb") as image_file:
            data = base64.b64encode(image_file.read()).decode()
            return data
    except Exception as e:
        print(f"Error loading image: {e}")
        return None
def render_dashboard(conn):
    # --- 1. AMBIL DATA DATABASE ---
    try:
        query = "SELECT * FROM daily_stock_log"
        df = pd.read_sql(query, conn)
        df['tanggal'] = pd.to_datetime(df['tanggal']).dt.date
    except Exception as e:
        st.error(f"Gagal mengambil data dari database: {e}")
        df = pd.DataFrame() 

    # --- 2. CSS ---
    st.markdown("""
        <style>
            .stApp { background-color: #F4F6F9; }

            /* Responsivitas Layar HP / Mobile */
            @media (max-width: 768px) {
                .block-container {
                    padding-top: 1.2rem !important;
                    padding-left: 0.8rem !important;
                    padding-right: 0.8rem !important;
                }
                .kpi-card, .alert-card {
                    padding: 14px 10px !important;
                    margin-bottom: 12px !important;
                }
                .kpi-title { font-size: 11px !important; }
                .kpi-value { font-size: 18px !important; }
                .tank-container {
                    width: 120px !important;
                    height: 200px !important;
                }
            }

            /* Header Styling */
            .adm-header { 
                background: linear-gradient(135deg, #ffffff, #f9fafb); 
                padding: 12px 16px !important;
                border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.04); 
                margin-bottom: 25px; 
                display: flex; 
                justify-content: space-between; 
                align-items: center;
                border-left: 6px solid #E3000F;
                border-bottom: 1px solid #E5E7EB;
            }
            .adm-title { 
                margin: 0; 
                color: #005A9E; 
                font-family: 'Segoe UI', Roboto, sans-serif;
                font-weight: 800;
                font-size: 16px !important;
            }
            
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 0 !important;
                margin-bottom: 15px;
            }

            /* KPI Card Styling (Modern Soft Elevation) */
            .kpi-card { 
                background-color: white; 
                padding: 18px 20px; 
                border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
                text-align: center; 
                border: 1px solid #EAEAEA;
                border-top: 4px solid #005A9E; 
                margin-bottom: 15px; 
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .kpi-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 18px rgba(0,0,0,0.08);
            }
            .kpi-title { 
                margin: 0; 
                color: #64748B; 
                font-size: 13px; 
                font-weight: 700; 
                text-transform: uppercase; 
                letter-spacing: 0.5px;
            }
            .kpi-value { 
                margin: 8px 0 0 0; 
                color: #1E293B; 
                font-size: 24px; 
                font-weight: 800; 
                font-variant-numeric: tabular-nums;
            }
            .kpi-green { color: #16A34A !important; }
            .kpi-orange { color: #EA580C !important; }
            
            /* Alert Card Styling */
            .alert-card { 
                background: linear-gradient(135deg, #DC2626, #B91C1C); 
                color: white; 
                padding: 18px 20px; 
                border-radius: 12px; 
                box-shadow: 0 4px 15px rgba(220, 38, 38, 0.25); 
                text-align: center; 
                margin-bottom: 15px; 
                transition: transform 0.2s ease;
            }
            .alert-card:hover {
                transform: translateY(-3px);
            }
            
            /* Digital Twin Tank Styling (Silinder Industri Realistis) */
            .tank-container { 
                width: 130px !important;
                height: 220px !important; 
                border: 3px solid #94A3B8; 
                border-radius: 16px; 
                position: relative; 
                background: linear-gradient(90deg, #E2E8F0 0%, #F8FAFC 50%, #CBD5E1 100%); 
                margin: 0 auto !important; 
                overflow: hidden; 
                box-shadow: inset 0 3px 8px rgba(0,0,0,0.15), 0 6px 14px rgba(0,0,0,0.06); 
            }
            /* Garis Ukur Level (Ruler 25%, 50%, 75%) */
            .tank-container::before {
                content: "";
                position: absolute;
                top: 0; left: 8px; bottom: 0; width: 14px;
                background: repeating-linear-gradient(
                    to bottom,
                    rgba(100, 116, 139, 0.4) 0px,
                    rgba(100, 116, 139, 0.4) 2px,
                    transparent 2px,
                    transparent 25%
                );
                z-index: 3;
                pointer-events: none;
            }
            .tank-fill { 
                position: absolute; 
                bottom: 0; 
                width: 100%; 
                background: linear-gradient(180deg, #38BDF8 0%, #0284C7 40%, #0369A1 100%); 
                transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1); 
                border-top: 2px solid #7DD3FC;
            }
            .tank-text { 
                position: absolute; 
                top: 40%; 
                width: 100%; 
                text-align: center; 
                font-weight: 800; 
                color: #FFFFFF; 
                text-shadow: 0 2px 4px rgba(0,0,0,0.7); 
                z-index: 4; 
                padding: 0 6px;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- 3. HEADER & FILTER TANGGAL ---

    col_date, _ = st.columns([3, 5])
    with col_date:
        st.markdown("### 🗓️ Tanggal")
        selected_date = st.date_input("📅 Tanggal", datetime.date.today(), label_visibility="collapsed")
    st.write("") 

    # --- 4. LOGIKA PEMROSESAN DATA ---
    df_hari_ini = df[df['tanggal'] == selected_date] if not df.empty else pd.DataFrame()
    
    df_kap1 = df_hari_ini[df_hari_ini['id_area'] == 'KAP-1'] if not df_hari_ini.empty else pd.DataFrame()
    df_kap2 = df_hari_ini[df_hari_ini['id_area'] == 'KAP-2'] if not df_hari_ini.empty else pd.DataFrame()
    k1_awal = df_kap1['stok_awal_level_meter'].sum() if not df_kap1.empty else 0
    k1_terima = df_kap1['total_pengisian'].sum() if not df_kap1.empty else 0
    k1_pakai = df_kap1['total_pemakaian'].sum() if ('total_pemakaian' in df_kap1.columns and not df_kap1.empty) else 0 
    k1_akhir = df_kap1['stok_akhir_level_meter'].sum() if not df_kap1.empty else 0
    k1_loss = df_kap1['loss_kalkulasi'].sum() if ('loss_kalkulasi' in df_kap1.columns and not df_kap1.empty) else 0
    k1_tank1 = df_kap1['tank1_level'].sum() if 'tank1_level' in df_kap1.columns and not df_kap1.empty else 0
    k1_tank2 = df_kap1['tank2_level'].sum() if 'tank2_level' in df_kap1.columns and not df_kap1.empty else 0
    k1_daily_tank = df_kap1['daily_tank_level'].sum() if 'daily_tank_level' in df_kap1.columns and not df_kap1.empty else 0
    k1_totalisator = df_kap1['totalisator_out_assy'].sum() if 'totalisator_out_assy' in df_kap1.columns and not df_kap1.empty else 0
    k2_awal = df_kap2['stok_awal_level_meter'].sum() if not df_kap2.empty else 0
    k2_terima = df_kap2['total_pengisian'].sum() if not df_kap2.empty else 0
    k2_pakai = df_kap2['total_pemakaian'].sum() if ('total_pemakaian' in df_kap2.columns and not df_kap2.empty) else 0
    k2_akhir = df_kap2['stok_akhir_level_meter'].sum() if not df_kap2.empty else 0
    k2_loss = df_kap2['loss_kalkulasi'].sum() if ('loss_kalkulasi' in df_kap2.columns and not df_kap2.empty) else 0


    # --- 5. TABS AREA (UI) ---
    tab1, tab2 = st.tabs(["📍 Area KAP 1", "📍 Area KAP 2"])
    kapasitas_max = 20000

    # ================= TAB 1: KAP 1 =================
    with tab1:
        st.write("### Data Operasional - KAP 1")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Stok Awal</p><h3 class='kpi-value'>{k1_awal:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Penerimaan</p><h3 class='kpi-value kpi-green'>+ {k1_terima:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Pemakaian</p><h3 class='kpi-value kpi-orange'>- {k1_pakai:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c4:
            if k1_loss > 0:
                st.markdown(f"""
                    <div class='alert-card'>
                        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Selisih Stok vs Level Meter</p>
                        <h2 style='margin: 10px 0; font-size: 32px;'>- {k1_loss:,.0f} L</h2>
                        <p style='margin: 0; font-size: 11px;'>⚠️ MISMATCH - CEK KEBOCORAN/SALAH INPUT</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='kpi-card' style='border-top: 4px solid #28a745;'>
                        <p class='kpi-title'>Selisih Stok vs Level Meter</p>
                        <h3 class='kpi-value kpi-green'>0 L</h3>
                        <p style='margin: 0; font-size: 11px; color: #28a745; font-weight: bold;'>✅ STATUS AMAN</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        
        st.markdown("<h4 style='text-align: center; color: #333; margin-bottom: 20px;'>Digital Twin - status Tangki KAP 1</h4>", unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color: #ECEFF1; padding: 10px; border-radius: 5px; width: fit-content; margin: 0 auto 30px auto; border: 1px solid #CFD8DC;">
                <p style='text-align: center; font-weight: bold; font-size: 16px; color: #005A9E; margin: 0;'>Totalisator OUT ASSY: {k1_totalisator:,.1f}</p>
            </div>
            """, unsafe_allow_html=True)

        # Mendefinisikan 4 kolom sebelum memanggilnya
        tank_col1, tank_col2, tank_col3, tank_col4 = st.columns(4)

        max_tank12 = 100.0
        max_daily = 1000.0
        max_total = 20000.0

        def render_twin_tank(nama, level_saat_ini, kapasitas_maksimal):
            persentase = min(int((level_saat_ini / kapasitas_maksimal) * 100), 100) if kapasitas_maksimal > 0 else 0
            
            return f"""
                <div style='text-align: center; margin-bottom: 10px; font-weight: bold; color: #475569;'>{nama}</div>
                <div class='tank-container' style='height: 250px; width: 140px;'>
                    <div class='tank-fill' style='height: {persentase}%;'></div>
                    <div class='tank-text' style='font-size: 15px;'>{level_saat_ini:,.1f}<br><span style='font-size:12px; font-weight: 600; opacity: 0.9;'>({persentase}%)</span></div>
                </div>
                """

        with tank_col1:
            st.markdown(render_twin_tank("TANK 1", k1_tank1, max_tank12), unsafe_allow_html=True)
        with tank_col2:
            st.markdown(render_twin_tank("TANK 2", k1_tank2, max_tank12), unsafe_allow_html=True)
        with tank_col3:
            st.markdown(render_twin_tank("DAILY TANK", k1_daily_tank, max_daily), unsafe_allow_html=True)
        with tank_col4:
            st.markdown(render_twin_tank("STORAGE TOTAL", k1_akhir, max_total), unsafe_allow_html=True)

    with tab2:
        st.write("### Data Operasional - KAP 2")
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Stok Awal</p><h3 class='kpi-value'>{k2_awal:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Penerimaan</p><h3 class='kpi-value kpi-green'>+ {k2_terima:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c3:
        
            st.markdown(f"<div class='kpi-card'><p class='kpi-title'>Pemakaian</p><h3 class='kpi-value kpi-orange'>- {k2_pakai:,.0f} L</h3></div>", unsafe_allow_html=True)
        with c4:
            if k2_loss > 0:
                st.markdown(f"""
                    <div class='alert-card'>
                        <p style='margin: 0; font-size: 13px; font-weight: bold;'>Selisih Stok vs Level Meter</p>
                        <h2 style='margin: 10px 0; font-size: 32px;'>- {k2_loss:,.0f} L</h2>
                        <p style='margin: 0; font-size: 11px;'>⚠️ MISMATCH</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='kpi-card' style='border-top: 4px solid #28a745;'>
                        <p class='kpi-title'>Selisih Stok vs Level Meter</p>
                        <h3 class='kpi-value kpi-green'>0 L</h3>
                        <p style='margin: 0; font-size: 11px; color: #28a745; font-weight: bold;'>✅ STATUS AMAN</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        
        persen_isi_k2 = min(int((k2_akhir / kapasitas_max) * 100), 100) if kapasitas_max > 0 else 0

        _, col_tank_k2, _ = st.columns([1, 2, 1])
        with col_tank_k2:
            st.markdown("<h4 style='text-align: center; color: #333;'>Storage Tank KAP 2</h4>", unsafe_allow_html=True)            
            st.markdown(f"""
                <div class='tank-container' style='height: 280px; width: 180px;'>
                    <div class='tank-fill' style='height: {persen_isi_k2}%;'></div>
                    <div class='tank-text'>Level Meter<br>{k2_akhir:,.0f} L<br><span style='font-size:13px; font-weight:600; opacity:0.9;'>({persen_isi_k2}%)</span></div>
                </div>
            """, unsafe_allow_html=True)