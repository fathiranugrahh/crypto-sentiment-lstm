import os
import gc
import numpy as np
import pandas as pd
import shap
import warnings
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

def evaluate_shap():
    print("="*60)
    print("RE-RUN: SHAP (XAI) Model LSTM - Pragmatic Path")
    print("Menerapkan Evaluasi Amplitudo Absolut pada Dimensi 3D Asli")
    print("="*60)

    # 1. Load Data & Model Asli (Bukan GHOST)
    try:
        model = load_model('30_STAGE6_MODEL_Final_LSTM.keras')
        X_train = np.load('27_STAGE6_X_train_3D.npy')
        X_test = np.load('28_STAGE6_X_test_3D.npy')
    except Exception as e:
        print(f"Gagal memuat dataset: {e}")
        return

    # Penamaan Fitur (Bahasa Indonesia sesuai input revisi User)
    feature_names = [
        'Total Likes', 'Total Retweets', 'Frekuensi Cuitan', 
        'Prob. Sentimen Positif', 'Prob. Sentimen Negatif', 'Prob. Sentimen Netral', 
        'Narasi Personal', 'Narasi Kebijakan (Gov)', 'Narasi Korporat (Corp)', 
        'Harga Open', 'Harga High', 'Harga Low', 'Harga Close', 'Momentum Volume 24H'
    ]

    # 2. Formating Background Data
    np.random.seed(42) 
    background_indices = np.random.choice(X_train.shape[0], 100, replace=False)
    background_3d = X_train[background_indices]
    test_samples_3d = X_test[:100]

    timesteps = background_3d.shape[1]
    features = background_3d.shape[2]

    # Menerjemahkan 3D ke 2D (Sesuai Syarat Input Opsi 2), Tanpa Dilusi di Awal
    background_2d = background_3d.reshape(background_3d.shape[0], -1) 
    test_samples_2d = test_samples_3d.reshape(test_samples_3d.shape[0], -1)

    def predict_lstm_wrapper(x):
        x_3d = x.reshape(x.shape[0], timesteps, features)
        return model.predict(x_3d, verbose=0).flatten()

    warnings.filterwarnings("ignore")
    background_summarized = shap.kmeans(background_2d, 10) 
    explainer = shap.KernelExplainer(predict_lstm_wrapper, background_summarized)
    
    print("Membongkar struktur asli gradien LSTM Pragmatic...")
    shap_values_raw = explainer.shap_values(test_samples_2d, nsamples=500, l1_reg="aic")

    # Kembalikan struktur vektor ke 3D asli
    shap_values_3d = shap_values_raw.reshape(-1, timesteps, features)

    # [INSTRUKSI REVISI KOSMETIK: THE CANCELLATION KILLER]
    # UBAH DARI: np.mean(shap_values_3d, axis=1)
    # MENJADI: np.mean(np.abs(shap_values_3d), axis=1)
    print("Menerapkan Agregasi Peak Impact (Max) np.abs() di sepanjang sumbu 24-jam...")
    mean_abs_temp = np.max(np.abs(shap_values_3d), axis=1) # <--- POIN MODIFIKASI UTAMA (Max Pooling)
    
    # Rata-rata akhir di seluruh array sampel (Untuk kebutuhan CSV)
    mean_abs_shap = np.mean(mean_abs_temp, axis=0)

    # Penskalaan matriks data asli untuk sumbu x Beeswarm plot
    test_samples_aggregated = np.mean(test_samples_3d, axis=1)

    # Setup Grafik
    plt.style.use('default')
    
    print("Men-generate 5_shap_summary.png...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(mean_abs_temp, test_samples_aggregated, feature_names=feature_names, plot_type="bar", show=False)
    plt.title("SHAP Peak Feature Impact (Max Pooling + Abs)", pad=20, fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('5_shap_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Men-generate 6_shap_beeswarm.png...")
    plt.figure(figsize=(10, 8))
    shap.summary_plot(mean_abs_temp, test_samples_aggregated, feature_names=feature_names, show=False)
    plt.title("SHAP Magnitude Dispersal (Peak Impact - Max)", pad=20, fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('6_shap_beeswarm.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Ekspor data CSV...")
    df_shap = pd.DataFrame({
        'Fitur_Input': feature_names,
        'Mean_Absolute_SHAP_Value': mean_abs_shap
    })
    
    df_shap = df_shap.sort_values(by='Mean_Absolute_SHAP_Value', ascending=False)
    df_shap.to_csv('hasil_shap_values.csv', index=False)

    print("\n[SUKSES] RE-RUN SHAP Pragmatic Path (Fix Cancellation) selesai dieksekusi!")

if __name__ == "__main__":
    evaluate_shap()


