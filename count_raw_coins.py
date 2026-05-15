import pandas as pd
import re
from collections import defaultdict

files = {
    'Elon Musk': '06_STAGE2_Valid_Elon.csv',
    'Michael Saylor': '07_STAGE2_Valid_Saylor.csv',
    'Donald Trump': '08_STAGE2_Valid_Trump.csv'
}

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

print("REKAP JUMLAH PENYEBUTAN KOIN DARI DATA NON-AGREGASI (FILE VALID)\n" + "="*60)

total_coins = defaultdict(int)

for person, file_path in files.items():
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        continue
        
    coin_mentions = defaultdict(int)
    
    for text in df['content'].dropna():
        text_lower = str(text).lower()
        
        if 'shiba inu' in text_lower:
            count = len(re.findall(r'\bshiba inu\b', text_lower))
            coin_mentions['Shiba Inu (SHIB)'] += count
            text_lower = re.sub(r'\bshiba inu\b', '', text_lower)
            
        for word, canonical in coin_dict.items():
            if word == 'shiba inu': continue
            count = len(re.findall(rf'\b{word}\b', text_lower))
            if count > 0:
                coin_mentions[canonical] += count

    print(f"\n{person}:")
    if not coin_mentions:
        print("  - Tidak menyebutkan koin apapun.")
    else:
        for coin, count in sorted(coin_mentions.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {coin}: {count}")
            total_coins[coin] += count

print("\n" + "="*60 + "\nTOTAL PENYEBUTAN KESELURUHAN DARI KETIGA TOKOH:")
for coin, count in sorted(total_coins.items(), key=lambda x: x[1], reverse=True):
    print(f"- {coin}: {count}")
