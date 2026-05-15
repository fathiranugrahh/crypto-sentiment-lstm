import pandas as pd
import numpy as np
from transformers import pipeline
import time
from tqdm import tqdm

print("=" * 60)
print("  TAHAP 4: SCORING SENTIMEN MENGGUNAKAN CRYPTOBERT")
print("=" * 60)

# 1. LOAD DATASET
print("Membaca z_LOG_MASTER_DATASET_SYNCED_V2.csv...")
df = pd.read_csv('z_LOG_MASTER_DATASET_SYNCED_V2.csv')

# 2. INISIALISASI MODEL (Fine-Tuned for Crypto Social Media)
print("Loading model ElKulako/cryptobert...")
sentiment_analyzer = pipeline(
    "text-classification",
    model="ElKulako/cryptobert",
    top_k=None,
    truncation=True,
    max_length=512,
    framework="pt"  # Hindari Keras TF crash bawaan
)

def score_single_text(text):
    text = text.strip()
    if not text or len(text) < 3:
        return None
    try:
        raw_scores = sentiment_analyzer(text)[0]
    except Exception:
        return None
    
    # Mapping label spesifik CryptoBERT -> Standar Proyek
    p_pos = next(item['score'] for item in raw_scores if item['label'] == 'Bullish')
    p_neg = next(item['score'] for item in raw_scores if item['label'] == 'Bearish')
    p_neu = next(item['score'] for item in raw_scores if item['label'] == 'Neutral')
    
    return (p_pos, p_neg, p_neu)

def score_aggregated_text(full_text):
    fragments = full_text.split('||')
    all_pos, all_neg, all_neu = [], [], []
    
    for frag in fragments:
        result = score_single_text(frag)
        if result is not None:
            all_pos.append(result[0])
            all_neg.append(result[1])
            all_neu.append(result[2])
            
    if not all_pos:
        return (0.0, 0.0, 1.0, 'neutral')
        
    mean_pos = np.mean(all_pos)
    mean_neg = np.mean(all_neg)
    mean_neu = np.mean(all_neu)
    
    # Pastikan total 1.0 (mesin floating point)
    total = mean_pos + mean_neg + mean_neu
    if total > 0:
        mean_pos /= total
        mean_neg /= total
        mean_neu /= total
        
    # KEPUTUSAN LABEL AKHIR (Fungsi ARGMAX murni sesuai skripsi point (a))
    labels = ['positive', 'negative', 'neutral']
    probs = [mean_pos, mean_neg, mean_neu]
    final_class = labels[np.argmax(probs)]
        
    return (mean_pos, mean_neg, mean_neu, final_class)

# 3. OPTIMASI PERFORMA: Cache Unik Teks
unique_texts = df['cleaned_content'].unique()
print(f"Ditemukan {len(unique_texts)} cluster narasi unik dari {len(df)} total baris.")
print("Memulai komputasi Probabilitas Sentimen (Transformers)...")

cache_scores = {}
start_time = time.time()

for text in tqdm(unique_texts, desc="Inferencing"):
    cache_scores[str(text)] = score_aggregated_text(str(text))

elapsed = time.time() - start_time
print(f"Inference selesai dalam {elapsed/60:.2f} menit.")

# 4. MEMASANGKAN HASIL (MAPPING CACHE)
print("Memasangkan fitur probabilitas ke dalam master tabel utama...")

def extract_from_cache(text, idx):
    return cache_scores.get(str(text), (0.0, 0.0, 1.0, 'neutral'))[idx]

df['prob_pos'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 0))
df['prob_neg'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 1))
df['prob_neu'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 2))
df['sentiment_class'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 3))

# 5. EXPORT FINAL
output_name = 'z_LOG_16_STAGE4_DATA_Scored_Sentimen.csv'
df.to_csv(output_name, index=False)

print(f"\n✅ SUCCESS! Dataset dengan Fitur Sentimen Tersimpan di: {output_name}")
print("\n--- DISTRIBUSI SENTIMEN FINAL (FUNGSI ARGMAX) ---")
print(df['sentiment_class'].value_counts())



