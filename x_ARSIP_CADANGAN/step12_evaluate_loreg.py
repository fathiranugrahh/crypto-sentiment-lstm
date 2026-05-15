import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix

def evaluate_baseline_model():
    print("\n" + "="*50)
    print("EVALUASI MODEL BASELINE (LOGISTIC REGRESSION)")
    print("="*50)

    # Langkah 1: Load Data & Model
    x_test_file = '18_LOREG_X_test.csv'
    y_test_file = '20_LOREG_y_test.csv'
    model_file = 'model_loreg_baseline.pkl'

    try:
        X_test = pd.read_csv(x_test_file)
        y_test_df = pd.read_csv(y_test_file)
        y_test = y_test_df.values.ravel()
        model = joblib.load(model_file)
        print(f"Data & Model berhasil dimuat. (Total Sampel Uji: {len(X_test)})")
    except Exception as e:
        print(f"Gagal memuat komponen: {e}")
        return

    # Langkah 2: Prediksi Kelas dan Probabilitas
    y_pred = model.predict(X_test)
    
    # Ambil probabilitas kelas positif (1) untuk ROC-AUC
    y_probs = model.predict_proba(X_test)[:, 1]

    # Langkah 3: Hitung Metrik Sesuai Proposal
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_probs)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # Format laporan
    print(f"\n[1] ACCURACY SCORE : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"[2] ROC-AUC SCORE  : {roc_auc:.4f}")
    
    print("\n[3] CONFUSION MATRIX:")
    print("      Prediksi: 0   Prediksi: 1")
    print(f"Asli: 0      {conf_matrix[0][0]:<10} {conf_matrix[0][1]}")
    print(f"Asli: 1      {conf_matrix[1][0]:<10} {conf_matrix[1][1]}")

    print("\n[4] CLASSIFICATION REPORT:")
    # Output report default format sangat rapih di terminal
    print(classification_report(y_test, y_pred, target_names=['Turun/Tetap (0)', 'Naik (1)']))
    print("="*50 + "\n")

if __name__ == "__main__":
    evaluate_baseline_model()


