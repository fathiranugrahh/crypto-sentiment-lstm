import numpy as np
from tensorflow.keras.models import load_model
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, confusion_matrix

def evaluate_lstm_model():
    print("\n" + "="*50)
    print("EVALUASI MODEL DEEP LEARNING (LSTM)")
    print("="*50)

    # Langkah 1: Load Model & Data
    try:
        model = load_model('27_MODEL_Final_LSTM.keras')
        X_test = np.load('23_LSTM_X_test.npy')
        y_test = np.load('25_LSTM_y_test.npy')
        print(f"Model & Dataset Uji (.npy) berhasil dimuat. (Total Sampel: {len(X_test)})\n")
    except Exception as e:
        print(f"Gagal memuat file: {e}")
        return

    # Langkah 2: Proses Prediksi (Probabilitas & Kelas Biner)
    print("Melakukan inferensi prediksi pada Testing Data...")
    
    # Model Sequential LSTM + Sigmoid mengeluarkan output probabilitas array 2D
    raw_predictions = model.predict(X_test, verbose=0)
    
    # Ekstrak / ratakan array probabilitas menjadi 1D
    y_pred_probs = raw_predictions.flatten()
    
    # Konversi probabilitas ke kelas biner 0/1 (Threshold 0.5)
    y_pred_classes = (y_pred_probs > 0.5).astype(int)

    # Langkah 3: Hitung Metrik Sesuai Proposal Skripsi
    accuracy = accuracy_score(y_test, y_pred_classes)
    roc_auc = roc_auc_score(y_test, y_pred_probs)
    conf_matrix = confusion_matrix(y_test, y_pred_classes)

    # Langkah 4: Formatting Output Terminal
    print(f"\n[1] ACCURACY SCORE : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"[2] ROC-AUC SCORE  : {roc_auc:.4f}")
    
    print("\n[3] CONFUSION MATRIX:")
    print("      Prediksi: 0   Prediksi: 1")
    print(f"Asli: 0      {conf_matrix[0][0]:<10} {conf_matrix[0][1]}")
    print(f"Asli: 1      {conf_matrix[1][0]:<10} {conf_matrix[1][1]}")

    print("\n[4] CLASSIFICATION REPORT:")
    print(classification_report(y_test, y_pred_classes, target_names=['Turun/Tetap (0)', 'Naik (1)']))
    print("="*50 + "\n")

if __name__ == "__main__":
    evaluate_lstm_model()


