import pandas as pd
import re
from collections import defaultdict

file_path = "10_STAGE2_DATA_Aggregated_622.csv"
df = pd.read_csv(file_path)

# Dictionary to map variations to a canonical coin name
coin_dict = {
    'bitcoin': 'Bitcoin (BTC)',
    'btc': 'Bitcoin (BTC)',
    'doge': 'Dogecoin (DOGE)',
    'dogecoin': 'Dogecoin (DOGE)',
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
    'polkadot': 'Polkadot (DOT)',
    'dot': 'Polkadot (DOT)',
    'polygon': 'Polygon (MATIC)',
    'matic': 'Polygon (MATIC)',
    'uniswap': 'Uniswap (UNI)',
    'uni': 'Uniswap (UNI)',
}

coin_mentions = defaultdict(int)

# Use regex to find whole words, ignoring case
# For 'shiba inu', we check it separately before checking 'shiba'
for text in df['content'].dropna():
    text_lower = text.lower()
    
    # Check multi-word coins first
    if 'shiba inu' in text_lower:
        count = len(re.findall(r'\bshiba inu\b', text_lower))
        coin_mentions['Shiba Inu (SHIB)'] += count
        # replace to avoid double counting with 'shiba'
        text_lower = re.sub(r'\bshiba inu\b', '', text_lower)
        
    for word, canonical in coin_dict.items():
        if word == 'shiba inu': continue # already handled
        count = len(re.findall(rf'\b{word}\b', text_lower))
        # Add to canonical
        coin_mentions[canonical] += count

print("DAFTAR KOIN DAN JUMLAH PENYEBUTAN:")
for coin, count in sorted(coin_mentions.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"- {coin}: {count}")

print(f"\nTotal jenis koin yang disebut: {sum(1 for c, v in coin_mentions.items() if v > 0)}")
