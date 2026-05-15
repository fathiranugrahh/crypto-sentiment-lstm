import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib

def train_baseline_logistic_regression():
    print("Memulai Pelatihan Model Baseline (Logistic Regression)...")
    
    # Langkah 1: Load Dataset Latih
    x_train_file = '22_STAGE5_X_train.csv'
    y_train_file = '19_LOREG_y_train.csv'
    
    try:
        X_train = pd.read_csv(x_train_file)
        y_train_df = pd.read_csv(y_train_file)
    except FileNotFoundError as e:
        print(f"Error: Dataset {e.filename} tidak ditemukan. Harap pastikan tahap sebelumnya selesai.")
        return
        
    # Konversi y_train menjadi array 1D untuk mencegah iterrows/numpy dimensionality warning di Scikit-Learn
    y_train = y_train_df['Tren_Harga_24H'].values.ravel()
    print(f"Dataset berhasil dimuat: X_train {X_train.shape}, y_train {y_train.shape}")
    
    # Langkah 2: Konfigurasi Model
    # max_iter=2000 agar tidak gagal konvergensi (ConvergenceWarning) karena adanya fitur bervariasi tinggi
    # random_state=42 agar hasil training dapat direproduksi dengan deterministik
    print("\nKonfigurasi LogReg: max_iter=2000, random_state=42")
    model = LogisticRegression(max_iter=2000, random_state=42)
    
    # Langkah 3: Pelatihan & Inspeksi
    print("Memulai proses fitting...")
    model.fit(X_train, y_train)
    
    print("\nPelatihan selesai!")
    print(f"Jumlah fitur yang dipelajari: {X_train.shape[1]}")
    print(f"Dimensi Koefisien Model (model.coef_): {model.coef_.shape}")
    
    # Langkah 4: Ekspor Model
    model_output_path = 'model_loreg_baseline.pkl'
    joblib.dump(model, model_output_path)
    print(f"\n[SUKSES] Model hasil prediksi berhasil diekspor secara utuh ke: {model_output_path}")

if __name__ == "__main__":
    train_baseline_logistic_regression()



