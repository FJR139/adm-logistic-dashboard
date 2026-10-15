import pandas as pd

# 1. Konfigurasi Nama File
FILE_EXCEL_INPUT = "data baru FAJAR.xlsx" # Ganti dengan nama file Excel Anda yang SUDAH ADA ANGKA-nya
FILE_CSV_OUTPUT = "hasil_konversi_kap1.csv"

print(f"Membaca file {FILE_EXCEL_INPUT}...")

try:
    # 2. Buka Sheet Excel
    df = pd.read_excel(FILE_EXCEL_INPUT, sheet_name='Sheet1')
    
    # List kosong untuk menampung data yang sudah rapi
    data_bersih = []

    # 3. Looping untuk membaca kolom tanggal (mulai dari indeks ke-4)
    # Kolom 0-3 diabaikan karena berisi label teks
    for col_idx in range(4, len(df.columns)):
        tanggal_kolom = df.columns[col_idx]
            
        # Validasi apakah nama header kolom adalah format tanggal (Timestamp)
        if isinstance(tanggal_kolom, pd.Timestamp):
            tgl_str = tanggal_kolom.strftime('%Y-%m-%d')
            
            try:
                # --- PROSES EKSTRAKSI DATA BERDASARKAN BARIS (INDEX DIMULAI DARI 0) ---
                # Ingat: Baris 3 di Excel = Index 2 di Python
                
                # A. Mengambil Data Stok
                stok_tanki_1 = df.iloc[2, col_idx] # Baris ke-3 (Tanki 1)
                stok_tanki_2 = df.iloc[3, col_idx] # Baris ke-4 (Tanki 2)
                
                # Membersihkan NaN menjadi 0
                stok_1 = 0 if pd.isna(stok_tanki_1) else float(stok_tanki_1)
                stok_2 = 0 if pd.isna(stok_tanki_2) else float(stok_tanki_2)
                
                # Total Stok Akhir KAP-1
                stok_akhir = stok_1 + stok_2
                
                # Jika stok di tanggal tersebut kosong/0, lewati (jangan dimasukkan ke CSV)
                if stok_akhir == 0:
                    continue
                
                # B. MENGAMBIL DATA LAIN (CONTOH)
                # Anda bisa menyesuaikan baris ini sesuai koordinat asli di file Excel Anda
                # Misalnya, Flowmeter RH & LH KAP 1 ada di baris 32 Excel (Index 31)
                pemakaian_rh_lh = df.iloc[31, col_idx]
                total_pemakaian = 0 if pd.isna(pemakaian_rh_lh) else float(pemakaian_rh_lh)
                
                # --- MENYIMPAN DATA KE LIST ---
                data_bersih.append({
                    "tanggal": tgl_str,
                    "id_area": "KAP-1",
                    "stok_awal_level_meter": 0, # Kosongkan atau isi dengan rumus jika ada
                    "total_pengisian": 0,       # Kosongkan atau isi dengan rumus jika ada
                    "total_pemakaian": total_pemakaian, 
                    "stok_akhir_level_meter": stok_akhir,
                    "loss_kalkulasi": 0,
                    "status_loss": "AMAN"
                })
                
                print(f"✔️ Berhasil mengekstrak data tanggal: {tgl_str}")
                
            except Exception as e:
                print(f"⚠️ Melewati kolom {tgl_str} karena ada data tidak wajar/error.")

    # 4. Export menjadi CSV
    if len(data_bersih) > 0:
        df_hasil = pd.DataFrame(data_bersih)
        # Export ke CSV tanpa menyertakan nomor index di pinggirnya
        df_hasil.to_csv(FILE_CSV_OUTPUT, index=False)
        print("\n✅ KONVERSI SELESAI!")
        print(f"Berhasil merakit {len(data_bersih)} baris data.")
        print(f"File CSV telah disimpan dengan nama: {FILE_CSV_OUTPUT}")
    else:
        print("\n❌ Gagal: Tidak ada data angka yang ditemukan (Semua stok bernilai 0 atau format tanggal salah).")

except FileNotFoundError:
    print(f"❌ ERROR: File '{FILE_EXCEL_INPUT}' tidak ditemukan di folder ini.")
except Exception as e:
    print(f"❌ ERROR FATAL: {e}")