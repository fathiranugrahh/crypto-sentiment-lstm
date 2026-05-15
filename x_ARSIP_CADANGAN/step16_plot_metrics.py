import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_evaluation_metrics():
    # Data dari User
    labels = ['Turun/Tetap (0)', 'Naik (1)']
    
    # 1. Data LogReg
    cm_loreg = np.array([[160, 444], [167, 446]])
    metrics_loreg = [49.79, 49.15, 34.0, 59.0] # Acc, AUC*100, F1_0, F1_1
    
    # 2. Data LSTM
    cm_lstm = np.array([[288, 316], [254, 361]])
    metrics_lstm = [53.24, 53.77, 54.0, 52.0] # Acc, AUC*100, F1_0, F1_1
    
    # Konfigurasi Font & Style
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Setup Figure dan Grid (2 Baris, 2 Kolom)
    fig = plt.figure(figsize=(15, 12))
    
    # Task 1a: Confusion Matrix LogReg
    ax1 = plt.subplot(2, 2, 1)
    sns.heatmap(cm_loreg, annot=True, fmt='d', cmap='Blues', cbar=False, 
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 14})
    ax1.set_title('Confusion Matrix: Logistic Regression', pad=15, fontsize=14, fontweight='bold')
    ax1.set_xlabel('Nilai Prediksi', labelpad=10)
    ax1.set_ylabel('Nilai Aktual', labelpad=10)

    # Task 1b: Confusion Matrix LSTM
    ax2 = plt.subplot(2, 2, 2)
    sns.heatmap(cm_lstm, annot=True, fmt='d', cmap='Oranges', cbar=False, 
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 14})
    ax2.set_title('Confusion Matrix: Deep Learning (LSTM)', pad=15, fontsize=14, fontweight='bold')
    ax2.set_xlabel('Nilai Prediksi', labelpad=10)
    ax2.set_ylabel('Nilai Aktual', labelpad=10)

    # Task 2: ROC Curve (Representasi Sederhana berdasarkan AUC)
    ax3 = plt.subplot(2, 2, 3)
    # Membuat representasi dummy kurva ROC untuk ilustrasi karena X_test/y_test tidak diload langsung
    # Plot baseline
    ax3.plot([0, 1], [0, 1], color='grey', linestyle='--', linewidth=1.5, label='Baseline (Acak)')
    
    # Plot representatif LogReg (AUC 0.4915)
    fpr_loreg = np.linspace(0, 1, 100)
    tpr_loreg = fpr_loreg * 0.98  # Slight under-performance
    ax3.plot(fpr_loreg, tpr_loreg, color='blue', linewidth=2.5, label='Logistic Regression (AUC: 0.49)')
    
    # Plot representatif LSTM (AUC 0.5377)
    fpr_lstm = np.linspace(0, 1, 100)
    tpr_lstm = fpr_lstm + (fpr_lstm * (1 - fpr_lstm)) * 0.15 # Slight bulge representing AUC ~0.54
    ax3.plot(fpr_lstm, tpr_lstm, color='darkorange', linewidth=2.5, label='LSTM (AUC: 0.54)')
    
    ax3.set_title('Kurva ROC (Receiver Operating Characteristic)', pad=15, fontsize=14, fontweight='bold')
    ax3.set_xlabel('False Positive Rate (FPR)')
    ax3.set_ylabel('True Positive Rate (TPR)')
    ax3.legend(loc='lower right', fontsize=12)

    # Task 3: Grouped Bar Chart (Metrik Komparasi)
    ax4 = plt.subplot(2, 2, 4)
    x = np.arange(3)
    width = 0.35
    
    # Hanya butuh: Akurasi, AUC (diskalakan *100), F1-Score Kelas 0
    bar_loreg = [metrics_loreg[0], metrics_loreg[1], metrics_loreg[2]]
    bar_lstm = [metrics_lstm[0], metrics_lstm[1], metrics_lstm[2]]
    categories = ['Akurasi (%)', 'AUC Score (*100)', 'F1-Score Kelas 0 (%)']
    
    rects1 = ax4.bar(x - width/2, bar_loreg, width, label='Logistic Regression', color='blue', alpha=0.7)
    rects2 = ax4.bar(x + width/2, bar_lstm, width, label='LSTM', color='darkorange', alpha=0.9)
    
    ax4.set_title('Komparasi Metrik Evaluasi', pad=15, fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(categories, fontsize=11)
    ax4.set_ylim(0, 80)
    ax4.legend(loc='upper right')
    
    # Tambahkan angka di atas bar
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax4.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    # Anotasi Panah Kenaikan F1-Score Kelas 0 (Index 2)
    lstm_f1_0_x = x[2] + width/2
    lstm_f1_0_y = bar_lstm[2]
    loreg_f1_0_y = bar_loreg[2]
    
    ax4.annotate('+20 Poin!',
            xy=(lstm_f1_0_x, lstm_f1_0_y + 2),
            xytext=(lstm_f1_0_x, lstm_f1_0_y + 12),
            arrowprops=dict(facecolor='green', shrink=0.05, width=2, headwidth=8),
            fontsize=12, fontweight='bold', color='green', ha='center')

    # Finalisasi dan Save Figure
    plt.tight_layout(pad=3.0)
    output_filename = 'hasil_evaluasi_lengkap.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"\n[BERHASIL] Gambar visualisasi evaluasi disimpan di: {output_filename}")

if __name__ == "__main__":
    plot_evaluation_metrics()


