import pandas as pd
from sklearn.model_selection import train_test_split

def temporal_train_test_split():
    print("Memulai Temporal Train-Test Split (80/20) untuk Logistic Regression...\n")
    
    # Langkah 1: Load Data yang Terskalakan
    x_file = 'X_scaled_loreg.csv'
    y_file = 'y_loreg.csv'
    
    try:
        X = pd.read_csv(x_file)
        y = pd.read_csv(y_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
        
    print(f"Data termuat! Total observasi: {len(X)}")
    
    # Langkah 2: Eksekusi Temporal Split
    # PENTING: shuffle=False untuk Data Time-Series guna mencegah Look-Ahead Bias
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        shuffle=False
    )
    
    # Langkah 3: Validasi & Ekspor
    print("\n[Validasi Dimensi Split]")
    print(f"X_train shape : {X_train.shape} ({len(X_train)/len(X)*100:.1f}%)")
    print(f"X_test shape  : {X_test.shape} ({len(X_test)/len(X)*100:.1f}%)")
    print(f"y_train shape : {y_train.shape} ({len(y_train)/len(y)*100:.1f}%)")
    print(f"y_test shape  : {y_test.shape} ({len(y_test)/len(y)*100:.1f}%)")
    
    # Menyimpan ke dalam CSV baru
    print("\nMenyimpan dataset train/test ke CSV...")
    X_train.to_csv('17_LOREG_X_train.csv', index=False)
    X_test.to_csv('18_LOREG_X_test.csv', index=False)
    y_train.to_csv('19_LOREG_y_train.csv', index=False)
    y_test.to_csv('20_LOREG_y_test.csv', index=False)
    
    print("Proses Selesai! File siap digunakan untuk training model.")

if __name__ == "__main__":
    temporal_train_test_split()


