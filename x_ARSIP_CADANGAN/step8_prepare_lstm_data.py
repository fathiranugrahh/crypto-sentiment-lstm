import pandas as pd
import numpy as np
import glob
import os

def build_lstm_panel_data():
    print("Membaca Master Dataset...")
    master_file = 'z_LOG_14b_DATA_Final_FE.csv'
    if not os.path.exists(master_file):
        print(f"Error: {master_file} tidak ditemukan!")
        return
        
    df = pd.read_csv(master_file)
    
    # 1. Tambah event_id unik
    df['event_id'] = range(len(df))
    
    # 2. Standarisasi Timestamp T=0
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.floor('h').dt.tz_localize(None)
    
    # 3. Vectorized Expansion (T-24 sampai T-1)
    # Membuat helper dataframe untuk offsets
    offsets = pd.DataFrame({'offset_hours': np.arange(-24, 0)})
    
    # Melakukan Cross Join (menciptakan 24 baris per event_id secara instan)
    print("Melakukan Expansion (Cross Join) untuk 24 jam histori...")
    df_panel = df.assign(key=1).merge(offsets.assign(key=1), on='key').drop('key', axis=1)
    
    # Kalkulasi hist_time secara vectorized
    df_panel['hist_time'] = df_panel['timestamp'] + pd.to_timedelta(df_panel['offset_hours'], unit='h')
    
    # 4. Global Price Indexing
    print("Memuat dan menggabungkan database harga...")
    price_files = glob.glob('*USDT_1h_prices.csv')
    df_prices_list = []
    
    for f in price_files:
        coin = os.path.basename(f).replace('USDT_1h_prices.csv', '')
        # Optimasi: Hanya load kolom yang dibutuhkan untuk join
        p_df = pd.read_csv(f, usecols=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        p_df['timestamp'] = pd.to_datetime(p_df['timestamp']).dt.tz_localize(None)
        p_df['target_coins'] = coin
        df_prices_list.append(p_df)
    
    # Gabungkan semua koin jadi satu lookup table
    df_price_lookup = pd.concat(df_prices_list, ignore_index=True)
    
    # 5. Vectorized Merge OHLCV
    print("Sinkronisasi data OHLCV historis...")
    # Kita overwrite kolom T=0 (open, high, low, close, volume) dengan data historis yang sesuai hist_time
    # Hapus dulu kolom OHLCV bawaan dari master agar tidak bentrok
    cols_to_remove = ['open', 'high', 'low', 'close', 'volume']
    df_panel = df_panel.drop(columns=cols_to_remove)
    
    df_final = pd.merge(
        df_panel,
        df_price_lookup,
        left_on=['target_coins', 'hist_time'],
        right_on=['target_coins', 'timestamp'],
        how='left',
        suffixes=('', '_lookup')
    )
    
    # 6. Sorting & Final Cleaning
    print("Sorting dan membersihkan dataset...")
    df_final = df_final.sort_values(by=['event_id', 'hist_time']).reset_index(drop=True)
    
    # Drop kolom temporer
    drop_list = ['timestamp_lookup', 'offset_hours']
    df_final = df_final.drop(columns=[c for c in drop_list if c in df_final.columns])
    
    # 7. Export
    output_file = 'z_LOG_dataset_lstm.csv'
    df_final.to_csv(output_file, index=False)
    
    print(f"\nSukses! Data panel LSTM siap di: {output_file}")
    print(f"Total baris: {len(df_final)} ({len(df)} peristiwa x 24 jam)")
    print(f"Null check (data bolong di bursa): \n{df_final[['close', 'volume']].isna().sum()}")

if __name__ == "__main__":
    build_lstm_panel_data()


