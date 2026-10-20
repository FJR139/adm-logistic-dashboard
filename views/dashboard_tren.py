import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

@st.cache_data(ttl=600, show_spinner="Mengambil data dari Database...")
def get_data_tren(_conn, tgl_mulai, tgl_selesai, area):
    query = """
        SELECT tanggal, id_area, stok_awal_level_meter, total_pengisian, 
               total_pemakaian, stok_akhir_level_meter, 
               loss_kalkulasi, status_loss, tank1_level, tank2_level, daily_tank_level
        FROM daily_stock_log
        WHERE tanggal BETWEEN %s AND %s
        AND id_area = %s
        ORDER BY tanggal ASC
    """
    return pd.read_sql_query(query, _conn, params=(tgl_mulai, tgl_selesai, area))

def render_dashboard_tren(conn):
    # --- CSS Khusus Tampilan Dashboard Tren ---
    st.markdown("""
        <style>
            @media (max-width: 600px) {
                .block-container {
                    padding-top: 1.2rem !important;
                    padding-bottom: 0.8rem !important;
                    padding-right: 0.8rem !important;
                }
            }

            [data-testid="column"]{
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 0 !important;
                margin-bottom: 12px;
            }
            .trend-summary-card {
                background: white;
                padding: 12px 10px !important;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 2px 6px rgba(0,0,0,0.03);
                text-align: center;
                border-top: 4px solid #005A9E;
            }
            .trend-summary-title {
                margin: 0;
                color: #64748B;
                font-size: 10px !important;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .trend-summary-val {
                margin: 6px 0 0 0;
                color: #1E293B;
                font-size: 18px !important;
                font-weight: 800;
            }
            .chart-container-box {
                background: white;
                padding: 15px !important;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.03);
                margin-bottom: 25px !important;
            }
            .chart-title-header {
                font-size: 16px !important;
                font-weight: 800;
                color: #1E293B;
                margin-bottom: 15px;
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #005A9E; font-weight: 800; margin-bottom: 5px;'>📈 Analisis Tren Historis BBM</h3>", unsafe_allow_html=True)
    st.caption("Pantau komposisi tangki, arus penerimaan/pemakaian, deviasi, serta pembandingan Stok Actual vs SAP.")
    st.write("---")

    # --- 1. Filter Periode Fleksibel ---
    col_mode, col_area = st.columns([3, 1])
    with col_mode:
        mode_periode = st.radio(
            "🗓️ Filter Periode Tampilan", 
            ["Harian (7 Hari)", "Mingguan (28 Hari)", "Bulanan (1 Bulan)", "Kustom Rentang"], 
            horizontal=True
        )
    with col_area:
        area = st.selectbox("📍 Pilih Area Operasional", ["KAP-1", "KAP-2"])

    tgl_hari_ini = datetime.now().date()

    if mode_periode == "Harian (7 Hari)":
        tgl_selesai = tgl_hari_ini
        tgl_mulai = tgl_hari_ini - timedelta(days=6)
    elif mode_periode == "Mingguan (28 Hari)":
        tgl_selesai = tgl_hari_ini
        tgl_mulai = tgl_hari_ini - timedelta(days=27)
    elif mode_periode == "Bulanan (1 Bulan)":
        tgl_selesai = tgl_hari_ini
        tgl_mulai = tgl_hari_ini - timedelta(days=29)
    else:
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            tgl_mulai = st.date_input("📅 Tanggal Mulai", tgl_hari_ini - timedelta(days=7))
        with col_d2:
            tgl_selesai = st.date_input("📅 Tanggal Selesai", tgl_hari_ini)
    
    st.write("")

    if conn:
        try:
            df = get_data_tren(conn, tgl_mulai, tgl_selesai, area)

            # Penambal otomatis kolom status_loss
            if not df.empty and 'loss_kalkulasi' in df.columns:
                df['status_loss'] = np.where(
                    df['loss_kalkulasi'].notna() & (df['loss_kalkulasi'].abs() > 0.01),
                    'SELISIH',
                    'AMAN'
                )

            if df.empty:
                st.warning(f"⚠️ Belum ada catatan data operasional untuk **{area}** pada rentang **{tgl_mulai.strftime('%d %b %Y')} - {tgl_selesai.strftime('%d %b %Y')}**.")
            else:
                df['tanggal'] = pd.to_datetime(df['tanggal'])
                df['tgl_str'] = df['tanggal'].dt.strftime('%d-%b')

                # Isi nilai null pada tangki dengan angka 0
                df['tank1_level'] = df['tank1_level'].fillna(0)
                df['tank2_level'] = df['tank2_level'].fillna(0)
                df['daily_tank_level'] = df['daily_tank_level'].fillna(0)

                # --- 2. Ringkasan Eksekutif (KPI Header) ---
                total_masuk = df['total_pengisian'].sum()
                total_keluar = df['total_pemakaian'].sum()
                rata_pemakaian = df['total_pemakaian'].mean()
                total_loss = df['loss_kalkulasi'].sum()

                # Hitung perbandingan dengan durasi periode sebelumnya yang sama panjangnya
                durasi_hari = (tgl_selesai - tgl_mulai).days + 1
                tgl_selesai_prev = tgl_mulai - timedelta(days=1)
                tgl_mulai_prev = tgl_selesai_prev - timedelta(days=durasi_hari - 1)
                
                df_prev = get_data_tren(conn, tgl_mulai_prev, tgl_selesai_prev, area)
                total_keluar_prev = df_prev['total_pemakaian'].sum() if not df_prev.empty else 0

                if total_keluar_prev > 0:
                    delta_pct = ((total_keluar - total_keluar_prev) / total_keluar_prev) * 100
                else:
                    delta_pct = 0.0

                if delta_pct > 0:
                    delta_html = f"<div style='font-size: 11px; color: #DC2626; font-weight: bold; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #E2E8F0;'>🔺 +{delta_pct:.1f}% vs Periode Lalu</div>"
                elif delta_pct < 0:
                    delta_html = f"<div style='font-size: 11px; color: #16A34A; font-weight: bold; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #E2E8F0;'>🔻 {delta_pct:.1f}% vs Periode Lalu</div>"
                else:
                    delta_html = "<div style='font-size: 11px; color: #6B7280; font-weight: bold; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #E2E8F0;'>- Pemakaian Stabil</div>"

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.markdown(f"""
                        <div class='trend-summary-card' style='border-top-color: #16A34A;'>
                            <p class='trend-summary-title'>Total Penerimaan</p>
                            <h3 class='trend-summary-val' style='color: #16A34A;'>+{total_masuk:,.0f} <span style='font-size:14px; color:#64748B;'>L</span></h3>
                        </div>
                    """, unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""
                        <div class='trend-summary-card' style='border-top-color: #EA580C;'>
                            <p class='trend-summary-title'>Total Pemakaian</p>
                            <h3 class='trend-summary-val' style='color: #EA580C;'>-{total_keluar:,.0f} <span style='font-size:14px; color:#64748B;'>L</span></h3>
                            {delta_html}
                        </div>
                    """, unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""
                        <div class='trend-summary-card' style='border-top-color: #005A9E;'>
                            <p class='trend-summary-title'>Rata-rata Pakai / Hari</p>
                            <h3 class='trend-summary-val'>{rata_pemakaian:,.0f} <span style='font-size:14px; color:#64748B;'>L/hari</span></h3>
                        </div>
                    """, unsafe_allow_html=True)
                with k4:
                    loss_color = "#DC2626" if total_loss < 0 else ("#16A34A" if total_loss == 0 else "#D97706")
                    loss_prefix = "" if total_loss <= 0 else "+"
                    st.markdown(f"""
                        <div class='trend-summary-card' style='border-top-color: {loss_color};'>
                            <p class='trend-summary-title'>Total Selisih (Loss)</p>
                            <h3 class='trend-summary-val' style='color: {loss_color};'>{loss_prefix}{total_loss:,.0f} <span style='font-size:14px; color:#64748B;'>L</span></h3>
                        </div>
                    """, unsafe_allow_html=True)

                st.write("")
                st.write("")

                # ================= GRAFIK 1: Volume Tank (Stacked Bar) =================
                st.markdown("<div class='chart-container-box'>", unsafe_allow_html=True)
                st.markdown("<div class='chart-title-header'>Volume Tank</div>", unsafe_allow_html=True)
                
                fig_vol = go.Figure()
                fig_vol.add_trace(go.Bar(x=df['tgl_str'], y=df['tank1_level'], name='Tank 1', marker_color='#595959'))
                fig_vol.add_trace(go.Bar(x=df['tgl_str'], y=df['tank2_level'], name='Tank 2', marker_color='#858585'))
                fig_vol.add_trace(go.Bar(x=df['tgl_str'], y=df['daily_tank_level'], name='Daily Tank', marker_color='#FFC000'))
                
                fig_vol.update_layout(
                    barmode='stack',
                    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
                    yaxis=dict(title='Volume (Liter)', gridcolor='#E2E8F0'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=20, b=40, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=350
                )
                st.plotly_chart(fig_vol, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= GRAFIK 2: IN-OUT Tank (Diverging Bar) =================
                st.markdown("<div class='chart-container-box'>", unsafe_allow_html=True)
                st.markdown("<div class='chart-title-header'>IN-OUT Tank</div>", unsafe_allow_html=True)
                
                fig_inout = go.Figure()
                fig_inout.add_trace(go.Bar(x=df['tgl_str'], y=df['total_pengisian'], name='Input from Pertamina', marker_color='#70AD47'))
                fig_inout.add_trace(go.Bar(x=df['tgl_str'], y=-df['total_pemakaian'], name='Production Consume', marker_color='#ED7D31'))
                
                fig_inout.update_layout(
                    barmode='relative',
                    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
                    yaxis=dict(title='Volume (Liter)', gridcolor='#E2E8F0', zerolinecolor='#475569', zerolinewidth=1.5),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=20, b=40, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=350
                )
                st.plotly_chart(fig_inout, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= GRAFIK 3: Deviation (liter) =================
                st.markdown("<div class='chart-container-box'>", unsafe_allow_html=True)
                st.markdown("<div class='chart-title-header'>Deviation</div>", unsafe_allow_html=True)
                
                labels_dev = [f"{v:,.0f}" if pd.notnull(v) and v != 0 else "" for v in df['loss_kalkulasi']]
                
                fig_dev = go.Figure()
                fig_dev.add_trace(go.Bar(
                    x=df['tgl_str'], 
                    y=df['loss_kalkulasi'], 
                    name='Deviation (liter)', 
                    marker_color='#9DC3E6',
                    text=labels_dev,
                    textposition='outside'
                ))
                
                fig_dev.update_layout(
                    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
                    yaxis=dict(title='Deviation (Liter)', gridcolor='#E2E8F0', zerolinecolor='#475569', zerolinewidth=1.5),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=30, b=40, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=350
                )
                st.plotly_chart(fig_dev, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ================= GRAFIK 4: Stock Actual vs SAP =================
                st.markdown("<div class='chart-container-box'>", unsafe_allow_html=True)
                st.markdown("<div class='chart-title-header'>Stock Actual vs SAP</div>", unsafe_allow_html=True)
                
                # Menghitung estimasi stok SAP (Stok Awal + Pengisian - Pemakaian)
                stok_sap = df['stok_awal_level_meter'] + df['total_pengisian'] - df['total_pemakaian']
                delta_sap = df['stok_akhir_level_meter'] - stok_sap

                fig_sap = go.Figure()
                fig_sap.add_trace(go.Bar(x=df['tgl_str'], y=df['stok_akhir_level_meter'], name='Actual', marker_color='#4472C4'))
                fig_sap.add_trace(go.Bar(x=df['tgl_str'], y=stok_sap, name='SAP', marker_color='#ED7D31'))
                
                # Garis merah selisih kumulatif di bagian bawah
                fig_sap.add_trace(go.Scatter(
                    x=df['tgl_str'], y=delta_sap, name='Delta Actual vs SAP',
                    mode='lines+markers', line=dict(color='#FF0000', width=2),
                    marker=dict(size=6, color='#FFFF00', line=dict(width=1.5, color='#FF0000'))
                ))

                fig_sap.update_layout(
                    barmode='group',
                    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
                    yaxis=dict(title='Volume (Liter)', gridcolor='#E2E8F0'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(t=20, b=40, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=360
                )
                st.plotly_chart(fig_sap, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # --- Tabel Data & Ekspor ---
                with st.expander("📁 Lihat Tabel Data Historis & Ekspor ke Excel"):
                    st.markdown(f"**Tabel Rincian Operasional {area} ({tgl_mulai.strftime('%d %b %Y')} - {tgl_selesai.strftime('%d %b %Y')})**")
                    df_export = df[['tanggal', 'id_area', 'stok_awal_level_meter', 'total_pengisian', 'total_pemakaian', 'stok_akhir_level_meter', 'loss_kalkulasi', 'status_loss']].copy()
                    st.dataframe(df_export, use_container_width=True)
                    csv_data = df_export.to_csv(index=False, sep=';').encode('utf-8')
                    st.download_button(
                        label="📥 Download Data Historis ke Excel",
                        data=csv_data,
                        file_name=f"Data_Historis_{area}_{tgl_mulai.strftime('%Y%m%d')}_{tgl_selesai.strftime('%Y%m%d')}.csv",
                        mime='text/csv',
                        type="primary"
                    )

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat memuat visualisasi tren: {e}")
    else:
        st.error("Koneksi database terputus.")