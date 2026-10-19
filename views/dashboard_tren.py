import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

@st.cache_data(ttl=600, show_spinner="Mengambil data dari Database...")
def get_data_tren(_conn, tgl_mulai, tgl_selesai, area):
    query = """
        SELECT tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss
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
                padding: 12px 10px 5px 10px !important;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 3px 10px rgba(0,0,0,0.03);
                margin-bottom: 21px !important;
            }
            .chart-title-header {
                font-size: 14px !important;
                font-weight: 700;
                color: #0F172A;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='color: #005A9E; font-weight: 800; margin-bottom: 5px;'>📈 Analisis Tren Historis BBM</h3>", unsafe_allow_html=True)
    st.caption("Pantau fluktuasi konsumsi, penerimaan armada tangki, serta audit selisih stok secara periodik.")
    st.write("---")

    # --- 1. Filter Pencarian Fleksibel ---
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
                df['tgl_str'] = df['tanggal'].dt.strftime('%d %b')

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
                
                st.write("")
                # --- 3. GRAFIK 1: Tren Penerimaan vs Pemakaian ---
                st.markdown("""
                    <div class='chart-container-box'>
                        <div class='chart-title-header'>📊 Perbandingan Arus BBM: Penerimaan vs Pemakaian Harian</div>
                """, unsafe_allow_html=True)

                fig1 = go.Figure()
                fig1.add_trace(go.Bar(
                    x=df['tgl_str'], 
                    y=df['total_pengisian'], 
                    name='Penerimaan (Tangki Masuk)', 
                    marker=dict(color='#16A34A', line=dict(color='#15803D', width=1)),
                    hovertemplate='<b>Tgl %{x}</b><br>Penerimaan: <b>%{y:,.0f} L</b><extra></extra>'
                ))
                fig1.add_trace(go.Bar(
                    x=df['tgl_str'], 
                    y=df['total_pemakaian'], 
                    name='Pemakaian (Keluar Produksi)', 
                    marker=dict(color='#EA580C', line=dict(color='#C2410C', width=1)),
                    hovertemplate='<b>Tgl %{x}</b><br>Pemakaian: <b>%{y:,.0f} L</b><extra></extra>'
                ))
                
                fig1.update_layout(
                    barmode='group',
                    bargap=0.25,
                    bargroupgap=0.1,
                    xaxis=dict(title='Tanggal', showgrid=False, tickfont=dict(size=12, color='#475569')),
                    yaxis=dict(title='Volume (Liter)', gridcolor='#F1F5F9', zerolinecolor='#CBD5E1', tickfont=dict(size=12, color='#475569')),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
                    margin=dict(t=30, b=30, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=340
                )
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # --- 4. GRAFIK 2 & 3: 2 Kolom Sejajar ---
                col_chart1, col_chart2 = st.columns(2)

                # --- GRAFIK 2: Garis Stok Bersambung ---
                with col_chart1:
                    st.markdown("""
                        <div class='chart-container-box'>
                            <div class='chart-title-header'>📉 Tren Sisa Stok Fisik (Level Meter)</div>
                    """, unsafe_allow_html=True)

                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=df['tgl_str'], 
                        y=df['stok_akhir_level_meter'],
                        mode='lines+markers',
                        name='Stok Akhir',
                        line=dict(color='#005A9E', width=3, shape='spline'),
                        marker=dict(size=7, color='#005A9E', line=dict(width=2, color='white')),
                        fill='tozeroy',
                        fillcolor='rgba(0, 90, 158, 0.08)',
                        connectgaps=True,
                        hovertemplate='<b>Tgl %{x}</b><br>Stok Level Meter: <b>%{y:,.0f} L</b><extra></extra>'
                    ))
                    fig2.update_layout(
                        xaxis=dict(title='Tanggal', showgrid=False, tickfont=dict(size=11, color='#475569')),
                        yaxis=dict(title='Volume Tangki (Liter)', gridcolor='#F1F5F9', tickfont=dict(size=11, color='#475569')),
                        margin=dict(t=20, b=30, l=10, r=10),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=320
                    )
                    st.plotly_chart(fig2, use_container_width=True, key="grafik_stok_tangki")
                    st.markdown("</div>", unsafe_allow_html=True)

                # --- GRAFIK 3: Selisih / Loss Harian ---
                with col_chart2:
                    st.markdown("""
                        <div class='chart-container-box'>
                            <div class='chart-title-header'>⚠️ Pantauan Selisih / Loss Kalkulasi</div>
                    """, unsafe_allow_html=True)

                    warna_list = ['#DC2626' if val < 0 else ('#16A34A' if val == 0 else '#2563EB') for val in df['loss_kalkulasi']]
                    
                    fig3 = go.Figure()
                    fig3.add_trace(go.Bar(
                        x=df['tgl_str'], 
                        y=df['loss_kalkulasi'], 
                        marker=dict(color=warna_list),
                        hovertemplate='<b>Tgl %{x}</b><br>Selisih: <b>%{y:,.1f} L</b><extra></extra>'
                    ))
                    fig3.add_hline(y=0, line_width=1.5, line_color="#475569")

                    fig3.update_layout(
                        xaxis=dict(title='Tanggal', showgrid=False, tickfont=dict(size=11, color='#475569')),
                        yaxis=dict(title='Loss / Selisih (Liter)', gridcolor='#F1F5F9', tickfont=dict(size=11, color='#475569')),
                        showlegend=False,
                        margin=dict(t=20, b=30, l=10, r=10),
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=320
                    )
                    st.plotly_chart(fig3, use_container_width=True, key="grafik_loss_selisih")
                    st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Terjadi kesalahan saat memuat visualisasi tren: {e}")
    else:
        st.error("Koneksi database terputus.")