import pandas as pd
from datetime import timedelta

# 1. Load Data
file_path = 'merged_social_crypto_2021_2025.csv'
df = pd.read_csv(file_path)
df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

# 2. Definisikan Tanggal Event
fomc_dates = [
    '2021-01-27', '2021-03-17', '2021-04-28', '2021-06-16', 
    '2021-07-28', '2021-09-22', '2021-11-03', '2021-12-15',
    '2022-01-26', '2022-03-16', '2022-05-04', '2022-06-15', 
    '2022-07-27', '2022-09-21', '2022-11-02', '2022-12-14',
    '2023-02-01', '2023-03-22', '2023-05-03', '2023-06-14', 
    '2023-07-26', '2023-09-20', '2023-11-01', '2023-12-13',
    '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12', 
    '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18',
    '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18', 
    '2025-07-30'
]

cpi_dates = [
    '2021-01-13', '2021-02-10', '2021-03-10', '2021-04-13', 
    '2021-05-12', '2021-06-10', '2021-07-13', '2021-08-11', 
    '2021-09-14', '2021-10-13', '2021-11-10', '2021-12-10',
    '2022-01-12', '2022-02-10', '2022-03-10', '2022-04-12', 
    '2022-05-11', '2022-06-10', '2022-07-13', '2022-08-10', 
    '2022-09-13', '2022-10-13', '2022-11-10', '2022-12-13',
    '2023-01-12', '2023-02-14', '2023-03-14', '2023-04-12', 
    '2023-05-10', '2023-06-13', '2023-07-12', '2023-08-10', 
    '2023-09-13', '2023-10-12', '2023-11-14', '2023-12-12',
    '2024-01-11', '2024-02-13', '2024-03-12', '2024-04-10', 
    '2024-05-15', '2024-06-12', '2024-07-11', '2024-08-14', 
    '2024-09-11', '2024-10-10', '2024-11-13', '2024-12-11',
    '2025-01-15', '2025-02-12', '2025-03-12', '2025-04-10', 
    '2025-05-13', '2025-06-11', '2025-07-15', '2025-08-12'
]

# 3. Buat Set Tanggal Terlarang (H-1, H, H+1)
blacklisted_dates = set()
for d_str in fomc_dates + cpi_dates:
    base_date = pd.to_datetime(d_str).date()
    blacklisted_dates.add(base_date - timedelta(days=1))
    blacklisted_dates.add(base_date)
    blacklisted_dates.add(base_date + timedelta(days=1))

# 4. Filter Data
initial_count = len(df)
df['date_only'] = df['timestamp'].dt.date
df_filtered = df[~df['date_only'].isin(blacklisted_dates)].copy()

# Buang kolom bantuan
df_filtered = df_filtered.drop(columns=['date_only'])

# 5. Save & Summary
df_filtered.to_csv('MASTER_DATASET_FILTERED.csv', index=False)

print(f"Data Awal: {initial_count}")
print(f"Data Setelah Filter (H-1, H, H+1 Event): {len(df_filtered)}")
print(f"Jumlah Baris Terhapus: {initial_count - len(df_filtered)}")
print("\nFile disimpan ke: MASTER_DATASET_FILTERED.csv")



