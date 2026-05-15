import pandas as pd
from transformers import pipeline
import time
from tqdm import tqdm

print("=" * 60)
print("  TAHAP 5: LABELING NARASI PADA ZERO-SHOT CLASSIFICATION")
print("=" * 60)

# 1. LOAD DATASET SEBELUMNYA
print("Membaca z_LOG_16_STAGE4_DATA_Scored_Sentimen.csv...")
df = pd.read_csv('z_LOG_16_STAGE4_DATA_Scored_Sentimen.csv')

# 2. INISIALISASI ZERO-SHOT MODEL (Distilled untuk kecepatan CPU)
print("Mempersiapkan model valhalla/distilbart-mnli-12-3...")
classifier = pipeline(
    "zero-shot-classification", 
    model="valhalla/distilbart-mnli-12-3", 
    framework="pt"
)

# Label linguistik untuk NLI yang direkayasa (Prompt Engineering) untuk memisahkan konteks opini vs kebijakan
candidate_labels = [
    "personal opinion, casual feeling, or individual philosophy",
    "public figure discussing government policy, macroeconomic regulation, or state laws",
    "public figure announcing corporate business strategy, firm investments, or company decision"
]

def map_label(bart_label):
    if bart_label == "personal opinion, casual feeling, or individual philosophy":
        return "personal"
    elif bart_label == "public figure discussing government policy, macroeconomic regulation, or state laws":
        return "gov"
    elif bart_label == "public figure announcing corporate business strategy, firm investments, or company decision":
        return "corp"
    return "personal" # Fallback

def classify_aggregated_narrative(full_text):
    fragments = full_text.split('||')
    detected_classes = set()
    
    for frag in fragments:
        frag = frag.strip()
        if len(frag) < 5:
            continue
            
        try:
            # Model secara otomatis mengurutkan label probabilitas dari tinggi ke rendah
            result = classifier(frag, candidate_labels)
            best_label = result['labels'][0]  # Ambil argmax/prob tertinggi
            detected_classes.add(map_label(best_label))
        except Exception:
            pass
            
    # Jika kosong sama sekali (error dsb), default ke personal
    if not detected_classes:
        detected_classes.add("personal")
        
    is_personal = 1 if "personal" in detected_classes else 0
    is_gov = 1 if "gov" in detected_classes else 0
    is_corp = 1 if "corp" in detected_classes else 0
        
    return (is_personal, is_gov, is_corp)

# 3. OPTIMASI CACHING (Hanya Eksekusi Kalimat Unik)
unique_texts = df['cleaned_content'].unique()
print(f"\nDitemukan {len(unique_texts)} cluster narasi unik dari {len(df)} total baris.")
print("Memulai Zero-Shot Inferencing (Multi-Hot Encoding untuk teks agregat)...")

cache_classes = {}
start_time = time.time()

for text in tqdm(unique_texts, desc="Inferencing BART"):
    cache_classes[str(text)] = classify_aggregated_narrative(str(text))

elapsed = time.time() - start_time
print(f"Inference tipe narasi selesai dalam {elapsed/60:.2f} menit.")

# 4. MAPPING MULTI-HOT KE DATASET UTAMA
print("Menyuntikan label Multi-Hot Encoding ke array dataset utama...")

def extract_from_cache(text, idx):
    return cache_classes.get(str(text), (0, 0, 0))[idx]

df['is_personal'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 0))
df['is_gov'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 1))
df['is_corp'] = df['cleaned_content'].apply(lambda x: extract_from_cache(x, 2))

# 5. EXPORT FINAL
output_name = '18_STAGE4_DATA_Tagged_Narrative.csv'
df.to_csv(output_name, index=False)

print(f"\n✅ SUCCESS! Dataset dengan Identitas Tipe Narasi Tersimpan di: {output_name}")
print("\n--- DISTRIBUSI KELAS TIPE NARASI (Bisa beririsan/Multi-Hot) ---")
print(f"Total Personal Events       : {df['is_personal'].sum()}")
print(f"Total Government Events     : {df['is_gov'].sum()}")
print(f"Total Corporate Events      : {df['is_corp'].sum()}")



