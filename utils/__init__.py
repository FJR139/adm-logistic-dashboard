def get_stok_awal(conn, area, tanggal):
    try:
        query = """
            SELECT stok_akhir_level_meter 
            FROM daily_stock_log 
            WHERE id_area = %s AND tanggal < %s AND stok_akhir_level_meter IS NOT NULL
            ORDER BY tanggal DESC 
            LIMIT 1
        """
        cur = conn.cursor()
        cur.execute(query, (area, tanggal))
        row = cur.fetchone()
        cur.close()
        if row and row[0] is not None:
            return float(row[0])
        return 0.0
    except Exception as e:
        return 0.0
