import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render_dashboard_tren(conn):
    # --- CSS Khusus Tampilan Dashboard Tren ---
    st.markdown("""
        <style>
            /* 1. KODE UTAMA UNTUK HP - Memaksa elemen menumpuk vertikal */
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

    # --- 1. Filter Pencarian ---
    col1, col2, col3 = st.columns(3)
    with col1:
        bulan_dict = {
            "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
            "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
            "September": 9, "Oktober": 10, "November": 11, "Desember": 12
        }
        # Default September jika data 2026
        default_month_idx = 8 if datetime.now().year == 2026 and datetime.now().month < 9 else datetime.now().month - 1
        bulan_nama = st.selectbox("🗓️ Pilih Bulan", list(bulan_dict.keys()), index=8)
        bulan_angka = bulan_dict[bulan_nama]

    with col2:
        tahun = st.selectbox("📅 Pilih Tahun", [2026, 2027], index=0)

    with col3:
        area = st.selectbox("📍 Pilih Area Operasional", ["KAP-1", "KAP-2"])

    st.write("")

    if conn:
        try:
            query = """ 
                SELECT tanggal, id_area, stok_awal_level_meter, total_pengisian, total_pemakaian, stok_akhir_level_meter, loss_kalkulasi, status_loss
                FROM daily_stock_log
                WHERE EXTRACT(MONTH FROM tanggal) = %s
                AND EXTRACT(YEAR FROM tanggal) = %s
                AND id_area = %s
                ORDER BY tanggal ASC
            """
            df = pd.read_sql(query, conn, params=(bulan_angka, tahun, area))

            if df.empty:
                st.warning(f"⚠️ Belum ada catatan data operasional untuk **{area}** pada periode **{bulan_nama} {tahun}**.")
            else:
                df['tanggal'] = pd.to_datetime(df['tanggal'])
                df['tgl_str'] = df['tanggal'].dt.strftime('%d %b')

                # --- 2. Ringkasan Eksekutif (KPI Header) ---
                total_masuk = df['total_pengisian'].sum()
                total_keluar = df['total_pemakaian'].sum()
                rata_pemakaian = df['total_pemakaian'].mean()
                total_loss = df['loss_kalkulasi'].sum()

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
                st.markdown(f"**Tabel Rincian Operasional {area} - Perioed {bulan_nama}{tahun}**")


                df_export = df[['tanggal', 'id_area', 'stok_awal_level_meter', 'total_pengisian', 'total_pemakaian', 'stok_akhir_level_meter', 'loss_kalkulasi', 'status_loss']].copy()


                st.dataframe(df_export, use_container_width=True)



                csv_data = df_export.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="📥 Download Data Historis ke Excel",
                    data=csv_data,
                    file_name=f"Data_Historis_{area}_{bulan_nama}{tahun}.csv",
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
                    xaxis=dict(
                        title='Tanggal',
                        showgrid=False,
                        tickfont=dict(size=12, color='#475569')
                    ),
                    yaxis=dict(
                        title='Volume (Liter)',
                        gridcolor='#F1F5F9',
                        zerolinecolor='#CBD5E1',
                        tickfont=dict(size=12, color='#475569')
                    ),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        font=dict(size=12)
                    ),
                    margin=dict(t=30, b=30, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=340
                )
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # --- 4. GRAFIK 2 & 3: 2 Kolom Sejajar ---
                col_chart1, col_chart2 = st.columns(2)

                # --- GRAFIK 2: Garis Stok Bersambung (Area Chart) ---
                with col_chart1:
                    st.markdown("""
                        <div class='chart-container-box'>
                            <div class='chart-title-header'>📉 Tren Sisa Stok Fisik (Level Meter)</div>
                    """, unsafe_allow_html=True)

                    # Buat grafik garis bersambung mulus dengan fill warna di bawah garis
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
                        connectgaps=True,  # Menyambung garis meskipun ada tanggal yang terlewati
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
                    # Garis batas 0 yang tegas
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