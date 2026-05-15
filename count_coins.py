import pandas as pd
import re
from collections import Counter

file_path = "10_STAGE2_DATA_Aggregated_622.csv"
df = pd.read_csv(file_path)

# List of common cryptocurrencies and their tickers to look for
# We will do case-insensitive word matching
coin_dict = {
    'bitcoin': 'Bitcoin (BTC)',
    'btc': 'Bitcoin (BTC)',
    'doge': 'Dogecoin (DOGE)',
    'dogecoin': 'Dogecoin (DOGE)',
    'ethereum': 'Ethereum (ETH)',
    'eth': 'Ethereum (ETH)',
    'shiba': 'Shiba Inu (SHIB)',
    'shib': 'Shiba Inu (SHIB)',
    'floki': 'Floki',
    'solana': 'Solana (SOL)',
    'sol': 'Solana (SOL)',
    'cardano': 'Cardano (ADA)',
    'ada': 'Cardano (ADA)',
    'avalanche': 'Avalanche (AVAX)',
    'avax': 'Avalanche (AVAX)',
    'chainlink': 'Chainlink (LINK)',
    'link': 'Chainlink (LINK)',
    'ripple': 'Ripple (XRP)',
    'xrp': 'Ripple (XRP)',
    'tron': 'Tron (TRX)',
    'trx': 'Tron (TRX)',
    'binance': 'Binance Coin (BNB)',
    'bnb': 'Binance Coin (BNB)',
    'litecoin': 'Litecoin (LTC)',
    'ltc': 'Litecoin (LTC)',
    'tether': 'Tether (USDT)',
    'usdt': 'Tether (USDT)',
    'terra': 'Terra (LUNA)',
    'luna': 'Terra (LUNA)'
}

# We also want to find any word that ends in 'coin' or starts with '#' just in case
hashtags = Counter()
words_ending_in_coin = Counter()
coin_mentions = Counter()

for text in df['content'].dropna():
    text_lower = text.lower()
    
    # Extract hashtags
    tags = re.findall(r'#(\w+)', text_lower)
    hashtags.update(tags)
    
    # Extract words ending in coin
    coin_words = re.findall(r'\b\w*coin\w*\b', text_lower)
    words_ending_in_coin.update(coin_words)
    
    # Count specific coins
    # We use regex word boundaries to avoid matching "eth" inside "something"
    for word, unified_name in coin_dict.items():
        # Handle special cases like "shiba inu"
        if word == "shiba":
            matches = len(re.findall(r'\bshiba(\s+inu)?\b', text_lower))
            coin_mentions[unified_name] += matches
        elif word == "shib":
            # skip shib if it's already counted in shiba? let's just count them independently then deduplicate later
            matches = len(re.findall(r'\bshib\b', text_lower))
            coin_mentions[unified_name] += matches
        else:
            matches = len(re.findall(rf'\b{word}\b', text_lower))
            coin_mentions[unified_name] += matches

print("Specific Coin Mentions:")
for coin, count in coin_mentions.most_common():
    if count > 0:
        print(f"{coin}: {count}")

print("\nTop 20 Hashtags:")
for tag, count in hashtags.most_common(20):
    print(f"#{tag}: {count}")

print("\nWords ending in 'coin':")
for word, count in words_ending_in_coin.most_common(10):
    print(f"{word}: {count}")
