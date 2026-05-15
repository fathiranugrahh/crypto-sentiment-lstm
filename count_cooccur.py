import pandas as pd
import re
from collections import defaultdict

file_path = "10_STAGE2_DATA_Aggregated_622.csv"
df = pd.read_csv(file_path)

coin_dict = {
    'bitcoin': 'Bitcoin (BTC)',
    'bitcoins': 'Bitcoin (BTC)',
    'btc': 'Bitcoin (BTC)',
    'doge': 'Dogecoin (DOGE)',
    'dogecoin': 'Dogecoin (DOGE)',
    'dogecoins': 'Dogecoin (DOGE)',
    'ethereum': 'Ethereum (ETH)',
    'eth': 'Ethereum (ETH)',
    'solana': 'Solana (SOL)',
    'sol': 'Solana (SOL)',
    'binance': 'Binance Coin (BNB)',
    'bnb': 'Binance Coin (BNB)',
    'cardano': 'Cardano (ADA)',
    'ada': 'Cardano (ADA)',
    'tron': 'Tron (TRX)',
    'trx': 'Tron (TRX)',
    'chainlink': 'Chainlink (LINK)',
    'link': 'Chainlink (LINK)',
    'xrp': 'Ripple (XRP)',
    'ripple': 'Ripple (XRP)',
    'avax': 'Avalanche (AVAX)',
    'avalanche': 'Avalanche (AVAX)',
    'shiba': 'Shiba Inu (SHIB)',
    'shiba inu': 'Shiba Inu (SHIB)',
    'shib': 'Shiba Inu (SHIB)',
    'floki': 'Floki',
    'litecoin': 'Litecoin (LTC)',
    'ltc': 'Litecoin (LTC)',
    'tether': 'Tether (USDT)',
    'usdt': 'Tether (USDT)',
    'terra': 'Terra (LUNA)',
    'luna': 'Terra (LUNA)'
}

# Untuk melihat agregasi tokoh
agg_mentions = defaultdict(lambda: defaultdict(int))

# Untuk melihat ko-okurensi koin dalam 1 hari (1 baris)
co_occurrence_counts = defaultdict(int)

print("Analisis Data Agregasi (10_STAGE2_DATA_Aggregated_622.csv)\n" + "="*60)

for index, row in df.iterrows():
    if pd.isna(row['content']) or pd.isna(row['username']):
        continue
        
    text_lower = str(row['content']).lower()
    uname = str(row['username']).strip()
    
    coins_in_this_row = set()
    
    if 'shiba inu' in text_lower:
        if len(re.findall(r'\bshiba inu\b', text_lower)) > 0:
            coins_in_this_row.add('Shiba Inu (SHIB)')
        text_lower = re.sub(r'\bshiba inu\b', '', text_lower)
            
    for word, canonical in coin_dict.items():
        if word == 'shiba inu': continue
        if len(re.findall(rf'\b{word}\b', text_lower)) > 0:
            coins_in_this_row.add(canonical)
            
    # Count how many DIFFERENT coins mentioned in this day
    if len(coins_in_this_row) > 0:
        co_occurrence_counts[len(coins_in_this_row)] += 1
        
    # Check if it's an aggregated user row
    if ',' in uname:
        for c in coins_in_this_row:
            # We count mentions by adding all occurrences? No, user asks how many coins.
            # Let's count mentions just like before to show the volume on aggregated days.
            pass # We'll do it separately

print("Dalam 'satu waktu' (1 baris data = 1 hari):")
for num_coins, count_days in sorted(co_occurrence_counts.items()):
    print(f"- Ada {count_days} hari di mana {num_coins} jenis koin disebut bersamaan.")

# Get exact dates where multiple coins were mentioned
print("\nContoh Hari dengan Penyebutan Lebih dari 1 Koin Bersamaan:")
count_printed = 0
for index, row in df.iterrows():
    if pd.isna(row['content']): continue
    text_lower = str(row['content']).lower()
    uname = str(row['username']).strip()
    timestamp = str(row['timestamp']).split()[0]
    
    coins_in_this_row = set()
    if 'shiba inu' in text_lower:
        if len(re.findall(r'\bshiba inu\b', text_lower)) > 0:
            coins_in_this_row.add('Shiba Inu (SHIB)')
        text_lower = re.sub(r'\bshiba inu\b', '', text_lower)
    for word, canonical in coin_dict.items():
        if word == 'shiba inu': continue
        if len(re.findall(rf'\b{word}\b', text_lower)) > 0:
            coins_in_this_row.add(canonical)
            
    if len(coins_in_this_row) > 1:
        print(f"[{timestamp}] oleh {uname}: {', '.join(coins_in_this_row)}")
        count_printed += 1

print(f"\nTotal ada {count_printed} hari di mana >1 koin disebut bersamaan.")

