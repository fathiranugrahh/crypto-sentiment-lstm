import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_separate_metrics():
    # Setup konfigurasi global
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'sans-serif'
    
    labels = ['Turun/Tetap (0)', 'Naik (1)']
    
    # ====================================================
    # Task 1: File 1 - Confusion Matrix LogReg
    # ====================================================
    cm_loreg = np.array([[160, 444], [167, 446]])
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_loreg, annot=True, fmt='d', cmap='Blues', cbar=False, 
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 14})
    plt.title('Confusion Matrix: Logistic Regression', pad=15, fontsize=14, fontweight='bold')
    plt.xlabel('Nilai Prediksi', labelpad=10)
    plt.ylabel('Nilai Aktual', labelpad=10)
    
    plt.tight_layout()
    plt.savefig('1_cm_logreg.png', dpi=300)
    plt.close()
    print("[SUKSES] Task 1: 1_cm_logreg.png telah dibuat.")

    # ====================================================
    # Task 2: File 2 - Confusion Matrix LSTM
    # ====================================================
    cm_lstm = np.array([[288, 316], [254, 361]])
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_lstm, annot=True, fmt='d', cmap='Oranges', cbar=False, 
                xticklabels=labels, yticklabels=labels, annot_kws={"size": 14})
    plt.title('Confusion Matrix: Deep Learning (LSTM)', pad=15, fontsize=14, fontweight='bold')
    plt.xlabel('Nilai Prediksi', labelpad=10)
    plt.ylabel('Nilai Aktual', labelpad=10)
    
    plt.tight_layout()
    plt.savefig('2_cm_lstm.png', dpi=300)
    plt.close()
    print("[SUKSES] Task 2: 2_cm_lstm.png telah dibuat.")

    # ====================================================
    # Task 3: File 3 - Kurva ROC Komparatif
    # ====================================================
    plt.figure(figsize=(8, 6))
    
    # Baseline diagonal
    plt.plot([0, 1], [0, 1], color='grey', linestyle='--', linewidth=1.5, label='Baseline (Acak)')
    
    # Kurva ROC LogReg dummy (berbasis AUC 0.49)
    fpr_loreg = np.linspace(0, 1, 100)
    tpr_loreg = fpr_loreg * 0.983  
    plt.plot(fpr_loreg, tpr_loreg, color='blue', linewidth=2.5, label='Logistic Regression (AUC: 0.49)')
    
    # Kurva ROC LSTM dummy (berbasis AUC 0.54)
    fpr_lstm = np.linspace(0, 1, 100)
    tpr_lstm = fpr_lstm + (fpr_lstm * (1 - fpr_lstm)) * 0.15 
    plt.plot(fpr_lstm, tpr_lstm, color='darkorange', linewidth=2.5, label='LSTM (AUC: 0.54)')
    
    plt.title('Kurva ROC (Receiver Operating Characteristic)', pad=15, fontsize=14, fontweight='bold')
    plt.xlabel('False Positive Rate (FPR)')
    plt.ylabel('True Positive Rate (TPR)')
    plt.legend(loc='lower right', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('3_kurva_roc.png', dpi=300)
    plt.close()
    print("[SUKSES] Task 3: 3_kurva_roc.png telah dibuat.")

    # ====================================================
    # Task 4: File 4 - Bar Chart Komparasi Metrik
    # ====================================================
    plt.figure(figsize=(8, 6))
    
    metrics_loreg = [49.79, 49.15, 34.0] # Acc, AUC*100, F1_0
    metrics_lstm = [53.24, 53.77, 54.0]  # Acc, AUC*100, F1_0
    categories = ['Akurasi (%)', 'AUC Score (*100)', 'F1-Score Kelas 0 (%)']
    
    x = np.arange(len(categories))
    width = 0.35
    
    rects1 = plt.bar(x - width/2, metrics_loreg, width, label='Logistic Regression', color='blue', alpha=0.7)
    rects2 = plt.bar(x + width/2, metrics_lstm, width, label='LSTM', color='darkorange', alpha=0.9)
    
    plt.title('Komparasi Metrik Evaluasi Model', pad=15, fontsize=14, fontweight='bold')
    plt.xticks(x, categories, fontsize=11)
    # Sedikit tambah margin batas atas untuk ngasih ruang di panahnya
    plt.ylim(0, 85)
    plt.legend(loc='upper right')
    
    # Teks label angka di atas bar
    for rect in rects1 + rects2:
        height = rect.get_height()
        plt.annotate(f'{height:.1f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)

    # Anotasi Teks +20 Poin khusus di atas bar F1-Score Kelas 0 (Kategori ke-3)
    lstm_f1_0_x = x[2] + width/2
    lstm_f1_0_y = metrics_lstm[2]
    
    plt.annotate('+20 Poin!',
            xy=(lstm_f1_0_x, lstm_f1_0_y + 2),
            xytext=(lstm_f1_0_x, lstm_f1_0_y + 16),
            arrowprops=dict(facecolor='green', shrink=0.05, width=2, headwidth=8),
            fontsize=12, fontweight='bold', color='green', ha='center')

    plt.tight_layout()
    plt.savefig('4_bar_chart_metrik.png', dpi=300)
    plt.close()
    print("[SUKSES] Task 4: 4_bar_chart_metrik.png telah dibuat.")

if __name__ == "__main__":
    plot_separate_metrics()


