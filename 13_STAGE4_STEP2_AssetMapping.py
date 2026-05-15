import pandas as pd
import re

print("="*60)
print("  TAHAP 2: PEMETAAN ASET KRIPTO (VOLATILITY SPILLOVER)")
print("="*60)

# 1. LOAD DATASET CLEANED
print("Membaca z_LOG_12_STAGE3_DATA_Cleaned_Text.csv...")
df_tweet = pd.read_csv('z_LOG_12_STAGE3_DATA_Cleaned_Text.csv')

# 2. DEFINISI ALGORITMA PEMETAAN (SESUAI TESIS)
TICKERS = ['ADA', 'AVAX', 'BNB', 'BTC', 'DOGE', 'ETH', 'LINK', 'SOL', 'TRX', 'XRP']

# Kategori 2: Tweet Umum & Makro Bitcoin (Volatility Spillover ke 10 koin)
macro_keywords = ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'web3', 'blockchain', 'defi', 'hodl', 'satoshi', '₿', 'market']

# Kategori 1: Tweet Spesifik (1 koin khusus)
specific_mapping = {
    'doge': ['DOGE'], 'dogecoin': ['DOGE'],
    'ethereum': ['ETH'], 'eth': ['ETH'],
    'solana': ['SOL'], 'sol': ['SOL'],
    'binance': ['BNB'], 'bnb': ['BNB'],
    'cardano': ['ADA'], 'ada': ['ADA'],
    'tron': ['TRX'], 'trx': ['TRX'],
    'chainlink': ['LINK'], 'link': ['LINK'],
    'xrp': ['XRP'], 'ripple': ['XRP'],
    'avax': ['AVAX'], 'avalanche': ['AVAX']
}

def map_text_to_assets(text):
    if not isinstance(text, str): 
        return []
        
    text_lower = text.lower()
    
    # 1. Cek Kategori Makro/Bitcoin
    for kw in macro_keywords:
        if kw in text_lower:
            return TICKERS # Berlaku untuk seluruh aset sampel
            
    # 2. Cek Kategori Spesifik Aset
    targets = set()
    for kw, coins in specific_mapping.items():
        if re.search(rf'\b{kw}\b', text_lower):
            for c in coins: 
                targets.add(c)
                
    # Jika tidak ada keyword yang terdeteksi, berasumsi ini cuitan makro/kebijakan umum influencer
    if not targets:
        return TICKERS
        
    return list(targets)

print("Mengklasifikasi dan Memetakan Target Koin...")
df_tweet['target_coins'] = df_tweet['cleaned_content'].apply(map_text_to_assets)

# 3. NORMALISASI ARRAY (EXPLODE)
# Satu narasi umum yang menargetkan TICKERS akan dipecah menjadi 10 baris terpisah
print("Menduplikasi baris berdasarkan array pemetaan (Explode)...")
df_mapped = df_tweet.explode('target_coins').dropna(subset=['target_coins'])

# 4. EXPORT
output_name = 'z_LOG_14_STAGE4_DATA_Mapped_Assets.csv'
df_mapped.to_csv(output_name, index=False)

print(f"\n✅ SUCCESS! Dataset Pemetaan Aset Tersimpan di: {output_name}")
print(f"Total baris awal: {len(df_tweet)}")
print(f"Total baris setelah pemetaan (Spillover Expansion): {len(df_mapped)}")



