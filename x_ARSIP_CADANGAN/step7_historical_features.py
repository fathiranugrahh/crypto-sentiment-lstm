import pandas as pd
import glob
import os

def generate_historical_features():
    print("Membaca Master Dataset (yang sudah ada Label Target)...")
    master_file = 'z_LOG_14b_DATA_Final_FE.csv'
    df_master = pd.read_csv(master_file)
    
    # 1. Standarisasi Waktu (Naive Datetime & Flooring)
    df_master['timestamp'] = pd.to_datetime(df_master['timestamp']).dt.tz_localize(None)
    df_master['t_0_floored'] = df_master['timestamp'].dt.floor('h')
    df_master['t_minus_24'] = df_master['t_0_floored'] - pd.Timedelta(hours=24)

    # 2. Loading & Concatenating Semua File Harga (Vectorized Lookup Source)
    print("Membangun Global Price Index...")
    price_files = glob.glob('*USDT_1h_prices.csv')
    df_prices_list = []
    
    for f in price_files:
        coin_name = os.path.basename(f).replace('USDT_1h_prices.csv', '')
        temp_df = pd.read_csv(f)
        temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp']).dt.tz_localize(None)
        temp_df['target_coins'] = coin_name
        # Kita cuma butuh close & volume buat T-24
        df_prices_list.append(temp_df[['target_coins', 'timestamp', 'close', 'volume']])
    
    df_price_lookup = pd.concat(df_prices_list, ignore_index=True)
    
    # 3. Vectorized Merge untuk T-24
    print("Menarik data T-24 menggunakan Vectorized Merge...")
    df_master = pd.merge(
        df_master, 
        df_price_lookup, 
        left_on=['target_coins', 't_minus_24'], 
        right_on=['target_coins', 'timestamp'],
        how='left',
        suffixes=('', '_t_minus_24')
    )

    # 4. Kalkulasi Persentase Perubahan (Vectorized)
    print("Menghitung return_24h dan vol_change_24h...")
    # Rumus: (T0 - T-24) / T-24
    df_master['return_24h'] = (df_master['close'] - df_master['close_t_minus_24']) / df_master['close_t_minus_24']
    
    # Pengamanan Volume 0 (Ganti 0 dengan NaN biar gak jadi INF)
    df_master['volume_t_minus_24'] = df_master['volume_t_minus_24'].replace(0, pd.NA)
    df_master['vol_change_24h'] = (df_master['volume'] - df_master['volume_t_minus_24']) / df_master['volume_t_minus_24']

    # 4.5 Data Cleaning (Hapus baris yang gagal dapet fitur T-24 atau hasilnya INF)
    initial_rows = len(df_master)
    df_master = df_master.replace([float('inf'), float('-inf')], pd.NA).dropna(subset=['return_24h', 'vol_change_24h'])
    dropped_rows = initial_rows - len(df_master)
    print(f"Filter Selesai: Menghapus {dropped_rows} baris karena data rumpang atau Volume=0 pada T-24.")

    # 5. Final Cleaning & Export
    # Drop kolom bantuan/temporer
    cols_to_drop = ['t_0_floored', 't_minus_24', 'timestamp_t_minus_24', 'close_t_minus_24', 'volume_t_minus_24']
    df_master = df_master.drop(columns=[c for c in cols_to_drop if c in df_master.columns])
    
    output_name = 'master_loreg.csv'
    df_master.to_csv(output_name, index=False)
    
    print(f"\nSelesai! File berhasil disimpan di: {output_name}")
    print(f"Statistik Fitur Baru:")
    print(df_master[['return_24h', 'vol_change_24h']].describe())

if __name__ == "__main__":
    generate_historical_features()


