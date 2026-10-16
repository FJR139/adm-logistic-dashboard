import pandas as pd

def get_stok_awal(conn, area, tanggal):
    try:
        query = "SELECT stok_akhir_level_meter FROM daily_stock_log WHERE id_area = %s AND tanggal < %s ORDER BY tanggal DESC LIMIT 1"
        df = pd.read_sql(query, conn, params=[area, tanggal])
        if not df.empty:
            return df.iloc[0]['stok_akhir_level_meter']
    except Exception as e:
            pass
            return 0