import csv
import time
import requests
import os
from datetime import datetime, timezone

# SYMBOLS: Replace DOT with HYPE. 
# Note: HYPE is very new, it won't have data from 2021 on Binance.
SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 
    'ADAUSDT', 'DOGEUSDT', 'TRXUSDT', 'LINKUSDT', 'HYPEUSDT'
]
INTERVAL = '1h'
START_DATE = "2021-01-01 00:00:00"
END_DATE = "2025-08-31 23:59:59"

def get_ms_timestamp(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def fetch_klines(symbol, start_ms, end_ms):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000 
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 400:
            return "NOT_FOUND"
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

def save_to_csv(symbol, data):
    filename = f"{symbol}_1h_prices.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        for k in data:
            ts = datetime.fromtimestamp(k[0]/1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([ts, k[1], k[2], k[3], k[4], k[5]])

def main():
    print("="*60)
    print("🚀 CRYPTO PRICE FETCHING (PER HOUR) - BINANCE API")
    print("="*60)
    print(f"Range: {START_DATE} to {END_DATE}")
    print("="*60)
    start_ms = get_ms_timestamp(START_DATE)
    end_ms = get_ms_timestamp(END_DATE)
    for symbol in SYMBOLS:
        print(f"\nProcessing {symbol}...")
        current_start = start_ms
        total_rows = 0
        while current_start < end_ms:
            data = fetch_klines(symbol, current_start, end_ms)
            if not data or data == "NOT_FOUND":
                break
            save_to_csv(symbol, data)
            total_rows += len(data)
            current_start = data[-1][6] + 1
            print(f"   -> Collected {total_rows} hours...", end='\r')
            time.sleep(0.1)
            if len(data) < 1000:
                break
        if total_rows > 0:
            print(f"\n✅ {symbol} DONE! Total: {total_rows} rows.")
        else:
            print(f"\n⚠️  {symbol} not found or no data on Binance.")

if __name__ == "__main__":
    main()


