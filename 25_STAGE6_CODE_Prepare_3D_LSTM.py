import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from tqdm import tqdm

def prepare_3d_tensor_lstm():
    print("Memulai Pemrosesan Data Time-Series 2D -> Tensor 3D untuk LSTM...\n")
    
    # Langkah 1: Load & Sorting
    lstm_file = 'z_LOG_24_STAGE6_DATA_2D_Flattened.csv'
    expected_cols = [
        'timestamp', 'username', 'content', 'likes', 'retweets', 'tweet_count', 
        'cleaned_content', 'target_coins', 'prob_pos', 'prob_neg', 'prob_neu', 
        'sentiment_class', 'is_personal', 'is_gov', 'is_corp', 'Tren_Harga_24H', 
        'event_id', 'hist_time', 'open', 'high', 'low', 'close', 'volume'
    ]
    try:
        # Load dataset tanpa header, pasang manual nama kolomnya
        df = pd.read_csv(lstm_file, header=None, names=expected_cols)
        print(f"Dataset dimuat. Total baris: {len(df)}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
        
    print("Sorting berdasarkan event_id dan hist_time...")
    # Parsing string datetime sangat penting untuk sorting yang akurat
    df['hist_time'] = pd.to_datetime(df['hist_time'])
    df = df.sort_values(by=['event_id', 'hist_time']).reset_index(drop=True)
    
    # Langkah 2: Handling Missing Values (ffill & bfill per event_id)
    print("Menambal (Imputasi) nilai NaN secara ffill dan bfill berdasarkan event_id...")
    cols_to_fill = ['open', 'high', 'low', 'close', 'volume']
    
    # Operasi groupby untuk mengisi Time-Series data agar tidak bocor ke peristiwa (koin) lain
    df[cols_to_fill] = df.groupby('event_id')[cols_to_fill].ffill()
    df[cols_to_fill] = df.groupby('event_id')[cols_to_fill].bfill()
    
    # Verifikasi kalau masih ada NaN yang tersisa
    if df[cols_to_fill].isna().sum().sum() > 0:
        print("PERINGATAN: Masih terdapat NaN setelah ffill & bfill. Baris kotor akan dikesampingkan di Langkah 5.")

    # Langkah 3: Feature Selection & Isolasi Target
    print("\nPemisahan target dan penghapusan fitur non-matematis...")
    # Cukup ambil nilai Target 1 kali per grup, karena 24 jam ini punya kunci target yang sama
    target_series = df.groupby('event_id')['Tren_Harga_24H'].first()
    
    # Drop kolom yang tidak relevan secara prediktif
    cols_to_drop = [
        'timestamp', 'hist_time', 'username', 'content', 
        'cleaned_content', 'target_coins', 'sentiment_class', 
        'Tren_Harga_24H'
    ]
    # Drop kolom yang ada saja (mencegah KeyError)
    df_features = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
    
    # Pastikan event_id dipertahankan sebagai alat ukur reshaper
    event_ids = df_features['event_id'].values
    df_features = df_features.drop(columns=['event_id'])
    
    # Langkah 4: Feature Scaling (MinMaxScaler)
    print("Melakukan Custom Scaling (MinMaxScaler) pada rentang (0,1)...")
    cols_to_scale = ['likes', 'retweets', 'tweet_count', 'open', 'high', 'low', 'close', 'volume']
    cols_to_scale = [col for col in cols_to_scale if col in df_features.columns]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('scaler', MinMaxScaler(feature_range=(0,1)), cols_to_scale)
        ],
        remainder='passthrough',
        verbose_feature_names_out=False
    )
    
    # Simpan nama kolom awal agar mudah jika di-debug nanti
    original_columns = df_features.columns
    
    # Fit & Transform ke semua baris
    X_scaled = preprocessor.fit_transform(df_features)
    
    # Langkah 5: Reshaping menjadi 3D Tensor
    print("\nMelakukan Reshape data 2D -> 3D Tensor (Samples, Timesteps, Features)...")
    df_scaled = pd.DataFrame(X_scaled, columns=preprocessor.get_feature_names_out())
    df_scaled['event_id'] = event_ids # Kembalikan ID untuk patokan struktur

    X_sequences = []
    y_sequences = []
    
    # Dapatkan ID yang unik, urutkan agar sesuai index `target_series`
    unique_events = target_series.index.tolist()
    
    # Validasi Ketat 24 Baris
    for event_id in tqdm(unique_events, desc="Validasi & Stacking"):
        group = df_scaled[df_scaled['event_id'] == event_id]
        
        # Cek apakah blok sekuensial lengkap persis 24 langkah dan bebas NaN
        if len(group) == 24 and not group.drop(columns=['event_id']).isna().any().any():
            # Ekstrak data mentah tanpa event_id (ubah jadi matriks Numpy)
            sequence = group.drop(columns=['event_id']).values
            X_sequences.append(sequence)
            y_sequences.append(target_series.loc[event_id])
            
    # Konversi list ke Array Numpy Murni
    X_3d = np.array(X_sequences)
    y_1d = np.array(y_sequences)
    
    print(f"\nReshape Selesai! Dimensi Tensor X : {X_3d.shape}")
    print(f"Reshape Selesai! Dimensi Target y : {y_1d.shape}")

    # Langkah 6: Temporal Train-Test Split (80:20)
    print("\nMelakukan pemecahan Temporal (Train/Test Split = 80/20) dengan mode Shuffle=False...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_3d, y_1d, 
        test_size=0.2, 
        shuffle=False
    )
    
    # Langkah 7: Ekspor ke Format NumPy (.npy)
    print("\n[Validasi Dimensi Akhir (Tensor NumPy)]")
    print(f"X_train_lstm : {X_train.shape} (Matriks Fitur Pelatihan)")
    print(f"y_train_lstm : {y_train.shape} (Label Target Pelatihan)")
    print(f"X_test_lstm  : {X_test.shape} (Matriks Fitur Pengujian)")
    print(f"y_test_lstm  : {y_test.shape} (Label Target Pengujian)")

    # Save to disk
    np.save('22_LSTM_X_train.npy', X_train)
    np.save('23_LSTM_X_test.npy', X_test)
    np.save('24_LSTM_y_train.npy', y_train)
    np.save('25_LSTM_y_test.npy', y_test)
    
    print("\nSelamat! Empat file '.npy' telah diekspor dan siap dimakan oleh arsitektur Keras keras/Tensorflow LSTM.")

if __name__ == "__main__":
    prepare_3d_tensor_lstm()



