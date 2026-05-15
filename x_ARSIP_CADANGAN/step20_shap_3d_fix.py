import os
import gc
import numpy as np
import pandas as pd
import shap
import warnings
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

def evaluate_shap_3d():
    print("="*60)
    print("STEP 20: PENGUKURAN SHAP 3D PRESISI & PEMBASMIAN CANCELLATION EFFECT")
    print("="*60)

    # 1. Load Data & Model
    try:
        model = load_model('27_MODEL_Final_LSTM.keras')
        X_train = np.load('22_LSTM_X_train.npy')
        X_test = np.load('23_LSTM_X_test.npy')
    except Exception as e:
        print(f"Gagal memuat dataset: {e}")
        return

    # Penamaan Fitur (Bahasa Indonesia Asli)
    feature_names = [
        'Total Likes', 'Total Retweets', 'Frekuensi Cuitan', 
        'Prob. Sentimen Positif', 'Prob. Sentimen Negatif', 'Prob. Sentimen Netral', 
        'Narasi Personal', 'Narasi Kebijakan (Gov)', 'Narasi Korporat (Corp)', 
        'Harga Open', 'Harga High', 'Harga Low', 'Harga Close', 'Momentum Volume 24H'
    ]

    # 2. Formating Data Tanpa Meratakan (Mean) di Awal
    np.random.seed(42) 
    background_indices = np.random.choice(X_train.shape[0], 100, replace=False)
    background_3d = X_train[background_indices]
    test_samples_3d = X_test[:100]

    timesteps = background_3d.shape[1]
    features = background_3d.shape[2]

    # Melakukan Flatten 3D -> 2D (Samples, 336) untuk kompabilitas tipe data input KernelExplainer 
    # Tanpa merata-rata / membuang nilai aslinya.
    background_2d = background_3d.reshape(background_3d.shape[0], -1) 
    test_samples_2d = test_samples_3d.reshape(test_samples_3d.shape[0], -1)

    # 3. Merakit Wrapper Presisi (Mengembalikan matriks ke 3D yang sah)
    def predict_lstm_wrapper(x):
        # x akan masuk dengan shape (n_samples, 336)
        x_3d = x.reshape(x.shape[0], timesteps, features)
        return model.predict(x_3d, verbose=0).flatten()

    print("Menjalankan perhitungan KernelExplainer dari 336 dimensi fitur independen temporal...")
    warnings.filterwarnings("ignore")
    
    # Inisialisasi K-Means Summarizer secara matematis direkomendasikan SHAP untuk background data 
    # di atas 100 dimensi agar menghindari jebakan singular matriks (Bug miliaran).
    background_summarized = shap.kmeans(background_2d, 10) 

    explainer = shap.KernelExplainer(predict_lstm_wrapper, background_summarized)
    
    # 4. Melakukan Kalkulasi dengan mengunci regularisasi regresi
    # Di sini rentang fluktuasi Sigmoid akan diukur pada 100 sampel ujicoba
    print("Membaca interaksi temporal per-jam (Proses berlangsung selama kurang lebih 2-3 Menit)...")
    shap_values_raw = explainer.shap_values(test_samples_2d, nsamples=500, l1_reg="aic")

    # 5. MENYELESAIKAN MASALAH CANCELLATION EFFECT
    # Kembalikan ke 3D (Samples, 24, 14)
    shap_values_3d = shap_values_raw.reshape(-1, timesteps, features)

    # DARI USER: "Lakukan agregasi menggunakan akumulasi margin absolut"
    # Menangkap amplitudo asli getaran getaran positif/negatif NLP per jam (tanpa saling membatalkan)
    mean_abs_temp = np.mean(np.abs(shap_values_3d), axis=1) # (100 Samples, 14 Fitur)
    
    # Menghitung Rata-rata akhir di seluruh sampel
    mean_abs_shap = np.mean(mean_abs_temp, axis=0)
    
    # Untuk kebutuhan bar plot dan beeswarm plot (membutuhkan 2D matriks sampel vs fitur)
    test_samples_aggregated = np.mean(test_samples_3d, axis=1)

    # 6. Generate Plot
    plt.style.use('default')
    
    print("Men-generate ulang 5_shap_summary.png...")
    plt.figure(figsize=(10, 8))
    # Menggunakan mean_abs_temp karena plot ini juga butuh agregasi dimensi absolut
    shap.summary_plot(mean_abs_temp, test_samples_aggregated, feature_names=feature_names, plot_type="bar", show=False)
    plt.title("SHAP Feature Importance (Fix Cancellation Effect by NLP Amplitude)", pad=20, fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig('5_shap_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Men-generate ulang 6_shap_beeswarm.png...")
    plt.figure(figsize=(10, 8))
    # Catatan: Beeswarm normalnya menunjukkan arah positif/negatif menggunakan SHAP asli, 
    # karena kita menyuguhkan matrix absolut untuk mencegah pembatalan, persebarannya akan bergeser murni di sumbu X positif (magnitude)
    shap.summary_plot(mean_abs_temp, test_samples_aggregated, feature_names=feature_names, show=False)
    plt.title("SHAP Magnitude Dispersal (Fix Cancellation Effect)", pad=20, fontsize=12, fontweight='bold')
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

    print("\n[SUKSES] Pengukuran 3D Opsi 2 (Total Modification SHAP Kernel) Selesai!")

if __name__ == "__main__":
    evaluate_shap_3d()


