import pandas as pd
import glob
import os

# 1. Cari semua file yang berakhiran _ML_READY.csv
file_list = glob.glob('*_ML_READY.csv')
print(f"Menemukan {len(file_list)} file koin siap gabung.")

all_dfs = []

# 2. Looping untuk membaca dan memberi label ticker
for file_path in file_list:
    # Ambil nama koin dari nama file (misal: BTC_ML_READY.csv -> BTC)
    ticker = os.path.basename(file_path).split('_')[0]
    
    print(f"Memproses {ticker}...")
    df = pd.read_csv(file_path)
    
    # 3. Buat kolom baru coin_ticker
    df['coin_ticker'] = ticker
    
    all_dfs.append(df)

# 4. Gabungkan (Concatenate)
if all_dfs:
    print("\nMenggabungkan seluruh koin menjadi satu dataset panel...")
    final_df = pd.concat(all_dfs, ignore_index=True)

    # 5. Simpan ke FINAL_ML_DATASET.csv
    output_name = 'FINAL_ML_DATASET.csv'
    final_df.to_csv(output_name, index=False)

    # 6. Verifikasi & Statistik
    print(f"\n--- RINGKASAN DATASET FINAL ---")
    print(f"Total Baris Gabungan: {len(final_df)}")
    print(f"File Output: {output_name}")
    print("\nDistribusi Baris per Koin:")
    print(final_df['coin_ticker'].value_counts())

    print("\nPreview 5 Baris Pertama:")
    cols_view = ['timestamp', 'coin_ticker', 'close', 'is_elon', 'is_saylor', 'is_trump', 'Tren_Harga_24H']
    print(final_df[cols_view].head())
else:
    print("Tidak ada file _ML_READY.csv ditemukan.")



