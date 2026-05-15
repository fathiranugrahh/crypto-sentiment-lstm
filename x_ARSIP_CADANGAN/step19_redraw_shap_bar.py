import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def redraw_shap_bar():
    # Bersihkan sisa plot di memory
    plt.clf()
    plt.close('all')

    # 1. Baca data SHAP murni berskala wajar
    try:
        df = pd.read_csv('hasil_shap_values.csv')
    except Exception as e:
        print(f"Gagal membaca CSV: {e}")
        return

    # Pandas barh plot akan menggambar dari bawah ke atas.
    # Agar fitur terkuat (High) berada di posisi paling atas, kita perlu me-reverse urutan dataframe.
    df_sorted = df.sort_values(by='Mean_Absolute_SHAP_Value', ascending=True)

    # Setup Kualitas Visual
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['font.family'] = 'sans-serif'
    
    # 2. Buat Kanvas Plotting Horizontal Bar
    plt.figure(figsize=(10, 8))
    
    # Plotting pakai Seaborn
    ax = sns.barplot(
        x='Mean_Absolute_SHAP_Value', 
        y='Fitur_Input', 
        data=df_sorted, 
        palette='viridis' # gradasi warna otomatis yang estetik
    )
    
    # 3. Label & Anotasi
    plt.title("SHAP Global Feature Importance", pad=20, fontsize=16, fontweight='bold')
    plt.xlabel('Mean Absolute SHAP Value (Dampak Klasifikasi Probabilitas 0-1)', fontsize=12, labelpad=10)
    plt.ylabel('Komponen Fitur Model', fontsize=12, labelpad=10)
    
    # Menambahkan grid minor biar lebih memanjakan mata dan terbaca presisi desimalnya
    ax.xaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

    # 4. Save Gambar Baru Menimpa yang Lama
    plt.tight_layout()
    plt.savefig('5_shap_summary.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("[SUKSES] Grafik 5_shap_summary.png berhasil di-redraw menggunakan skala wajar!")

if __name__ == "__main__":
    redraw_shap_bar()


