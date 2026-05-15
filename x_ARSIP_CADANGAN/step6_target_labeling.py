import pandas as pd
from datetime import timedelta
import os
from tqdm import tqdm

def label_target_variables():
    print("Starting Target Variable Labeling (Tren_Harga_24H)...")
    
    # 1. Load the tagged dataset
    input_file = '13b_DATA_Tagged.csv'
    output_file = 'z_LOG_14b_DATA_Final_FE.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
        
    df = pd.read_csv(input_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 2. Prepare Price Data Dictionary for fast lookup
    # Only load assets that are present in the dataset
    assets = df['target_coins'].unique()
    price_dfs = {}
    
    print("Loading price data files...")
    for asset in assets:
        price_file = f"{asset}USDT_1h_prices.csv"
        if os.path.exists(price_file):
            p_df = pd.read_csv(price_file)
            p_df['timestamp'] = pd.to_datetime(p_df['timestamp'])
            # Set index for fast lookup
            p_df.set_index('timestamp', inplace=True)
            price_dfs[asset] = p_df
        else:
            print(f"Warning: Price file for {asset} not found.")

    # 3. Calculation Logic
    t24_prices = []
    runups = []
    targets = []
    
    print("Calculating T+24 prices and labels...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        asset = row['target_coins']
        t0_ts = row['timestamp']
        # Floor to the beginning of the hour to match OHLCV index
        t0_ts_floored = t0_ts.replace(minute=0, second=0, microsecond=0).replace(tzinfo=None)
        
        t24_ts = t0_ts_floored + timedelta(hours=24)
        
        price_t0 = row['close'] # Use the price already synced at T=0
        price_t24 = None
        
        if asset in price_dfs:
            try:
                # Direct lookup in the indexed price dataframe
                price_t24 = price_dfs[asset].loc[t24_ts, 'close']
            except KeyError:
                # If exact T+24 hour is missing, try to find the nearest one within 2 hours
                # or leave it as NaN
                price_t24 = None
        
        if price_t24 is not None:
            runup = (price_t24 - price_t0) / price_t0
            target = 1 if price_t24 > price_t0 else 0
        else:
            runup = None
            target = None
            
        t24_prices.append(price_t24)
        runups.append(runup)
        targets.append(target)
    
    # 4. Add columns and save
    df['price_t24'] = t24_prices
    df['Price_Runup_24H'] = runups
    df['Tren_Harga_24H'] = targets
    
    # Remove rows where T+24 data is missing (end of dataset or gaps)
    initial_len = len(df)
    df.dropna(subset=['Tren_Harga_24H'], inplace=True)
    final_len = len(df)
    
    df.to_csv(output_file, index=False)
    print(f"Success! Final dataset saved to {output_file}")
    print(f"Rows dropped due to missing T+24 data: {initial_len - final_len}")
    print(f"Distribution of target class: \n{df['Tren_Harga_24H'].value_counts()}")

if __name__ == "__main__":
    label_target_variables()


