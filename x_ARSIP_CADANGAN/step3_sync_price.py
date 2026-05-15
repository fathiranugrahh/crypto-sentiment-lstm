import pandas as pd
import os

print("="*60)
print("  TAHAP 3: SINKRONISASI DENGAN HARGA PASAR AWAL (T=0)")
print("="*60)

# 1. LOAD DATASET MAPPED
print("Membaca z_LOG_11b_DATA_Mapped.csv...")
df_tweet_exploded = pd.read_csv('z_LOG_11b_DATA_Mapped.csv')

# Format waktu
df_tweet_exploded['timestamp'] = pd.to_datetime(df_tweet_exploded['timestamp'], utc=True)
# Pembulatan jam ke bawah untuk T=0 (Candle terdekat)
df_tweet_exploded['hour_rounded'] = df_tweet_exploded['timestamp'].dt.floor('h')

# 2. KONSOLIDASI 10 FILE OHLCV BINANCE
print("Memuat riwayat OHLCV 1H Binance dari 10 Koin...")
TICKERS = ['ADA', 'AVAX', 'BNB', 'BTC', 'DOGE', 'ETH', 'LINK', 'SOL', 'TRX', 'XRP']
all_price_data = []

for coin in TICKERS:
    file_path = f"{coin}USDT_1h_prices.csv"
    if not os.path.exists(file_path):
        continue
        
    df_p = pd.read_csv(file_path)
    df_p['timestamp'] = pd.to_datetime(df_p['timestamp'], utc=True)
    df_p = df_p.sort_values('timestamp').set_index('timestamp')
    
    # Menyimpan Harga Aktual Saat Narasi Dicuitkan (T=0)
    df_p = df_p.reset_index()
    df_p['target_coins'] = coin
    
    # Mengambil komponen OHLCV murni
    cols_to_keep = ['timestamp', 'target_coins', 'open', 'high', 'low', 'close', 'volume']
    all_price_data.append(df_p[cols_to_keep])

# Stack Seluruh Harga (Satu Tabel Panjang)
df_master_price = pd.concat(all_price_data, ignore_index=True)

# 3. FINAL INNER JOIN (Titik Acuan Peristiwa)
print("Penyatuan dataset narasi dengan harga (INNER JOIN)...")
final_df = pd.merge(
    df_tweet_exploded, 
    df_master_price, 
    left_on=['hour_rounded', 'target_coins'], 
    right_on=['timestamp', 'target_coins'],
    how='inner'  # Memastikan setiap Narasi HANYA tersinkron pada saat event terjadi
)

# Pembersihan format
final_df = final_df.drop(columns=['timestamp_y', 'hour_rounded']).rename(columns={'timestamp_x': 'timestamp'})

# 4. EXPORT
output_name = 'z_LOG_MASTER_DATASET_SYNCED_V2.csv'
final_df.to_csv(output_name, index=False)

print(f"\n✅ SUCCESS! Master Dataset Sinkronisasi Siap di: {output_name}")
print(f"Total baris agregat harga & momen (T=0): {len(final_df)}")


