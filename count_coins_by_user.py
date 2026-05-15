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
    'luna': 'Terra (LUNA)',
}

# user_mentions[username][coin_name] = count
user_mentions = defaultdict(lambda: defaultdict(int))
coin_total = defaultdict(int)

# In the dataset, sometimes 'username' column might have combined usernames like "elonmusk, saylor" 
# or they might be independent rows. I'll split the username field by comma just in case, but let's check
# the data. Wait, looking at row 18 in previous preview: "elonmusk, saylor" is actually a single string
# meaning it's an aggregated tweet. 
# But wait, looking at the dataset name `DATA_Aggregated_622.csv`, maybe it aggregated tweets per day?
# If username is "elonmusk, saylor", it means both mentioned it? Let's just track the string as-is, 
# or maybe check if there are combinations. 
# Actually, if username is 'elonmusk, saylor', we can split it.
# Wait, let's just use the 'username' string but if it contains commas, we split it so we count per individual user.
# But let's see. If the tweet count is aggregated per day, one row might contain tweets from both. 
# But wait, we can't easily attribute WHICH tweet belonged to who in that combined row. 
# So we should report the username string as is ("elonmusk", "saylor", "elonmusk, saylor", etc.)
# Or I can split it and attribute the mentions equally? No, let's just group by the exact 'username' value first.

for index, row in df.iterrows():
    if pd.isna(row['content']) or pd.isna(row['username']):
        continue
    
    text_lower = row['content'].lower()
    uname = str(row['username']).strip()
    
    # Handle shiba inu
    if 'shiba inu' in text_lower:
        count = len(re.findall(r'\bshiba inu\b', text_lower))
        user_mentions[uname]['Shiba Inu (SHIB)'] += count
        coin_total['Shiba Inu (SHIB)'] += count
        text_lower = re.sub(r'\bshiba inu\b', '', text_lower)
        
    for word, canonical in coin_dict.items():
        if word == 'shiba inu': continue
        count = len(re.findall(rf'\b{word}\b', text_lower))
        if count > 0:
            user_mentions[uname][canonical] += count
            coin_total[canonical] += count

print("DAFTAR PENYEBUTAN BERDASARKAN USER:")
for uname, counts in user_mentions.items():
    print(f"\nUser: {uname}")
    for coin, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {coin}: {count}")

print("\n--- REKAP TOTAL ---")
for coin, count in sorted(coin_total.items(), key=lambda x: x[1], reverse=True):
    print(f"{coin}: {count}")
