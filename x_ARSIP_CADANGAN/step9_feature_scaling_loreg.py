import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

def scale_features_loreg():
    print("Memulai Feature Selection & Scaling untuk Logistic Regression...")
    
    # Langkah 1: Isolasi Dataframe Induk
    master_file = 'master_loreg.csv'
    df_master = pd.read_csv(master_file)
    print(f"Dataset dimuat. Total baris awal: {len(df_master)}")

    # Langkah 2: Pembuatan Matriks X dan Target y
    # Pastikan membuang baris yang targetnya NaN (jika ada) demi keamanan
    df_master = df_master.dropna(subset=['Tren_Harga_24H'])
    
    y = df_master['Tren_Harga_24H'].values
    
    cols_to_drop = [
        'timestamp', 'username', 'content', 'cleaned_content', 
        'target_coins', 'sentiment_class', 
        'open', 'high', 'low', 'close', 'volume', 'event_id'
    ]
    
    # Drop kolom yang tidak perlu, dengan handle_errors (errors='ignore' menghindari error jika kolom tidak ada)
    X = df_master.drop(columns=cols_to_drop, errors='ignore')
    
    # Lepas juga variabel y dari matriks X
    if 'Tren_Harga_24H' in X.columns:
        X = X.drop(columns=['Tren_Harga_24H'])

    print(f"Bentuk Matriks X (Fitur): {X.shape}")
    print(f"Daftar Kolom X awal: {list(X.columns)}")

    # Langkah 3: Feature Scaling Berbasis ColumnTransformer
    cols_to_scale = ['likes', 'retweets', 'tweet_count', 'return_24h', 'vol_change_24h']
    
    # Pastikan kolom-kolom ini benar-benar ada di matriks X
    cols_to_scale = [col for col in cols_to_scale if col in X.columns]
    
    # Setup ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('scaler', StandardScaler(), cols_to_scale)
        ],
        remainder='passthrough',
        verbose_feature_names_out=False # Agar nama fitur asli (seperti 'prob_pos') tidak ditambah awalan 'remainder__'
    )
    
    print(f"Kolom yang akan di-scaling (StandardScaler): {cols_to_scale}")
    
    # Fitting & Transforming
    X_scaled_numpy = preprocessor.fit_transform(X)
    
    # Mengembalikan ke bentuk DataFrame Pandas (X_scaled_df)
    # preprocessor.get_feature_names_out() otomatis mengambil nama asli karena parameter verbose_feature_names_out=False
    feature_names = preprocessor.get_feature_names_out()
    X_scaled_df = pd.DataFrame(X_scaled_numpy, columns=feature_names)
    
    print("\nScaling Selesai!")
    print("Contoh 3 baris pertama dari X_scaled_df:")
    print(X_scaled_df.head(3))
    
    # Simpan hasil untuk dipakai di tahap modeling
    output_features = 'X_scaled_loreg.csv'
    output_target = 'y_loreg.csv'
    X_scaled_df.to_csv(output_features, index=False)
    pd.DataFrame(y, columns=['Tren_Harga_24H']).to_csv(output_target, index=False)
    print(f"\nDisimpan ke: {output_features} dan {output_target}")
    
    return X_scaled_df, y

if __name__ == "__main__":
    X_scaled, y_target = scale_features_loreg()


