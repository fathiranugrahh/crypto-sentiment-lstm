# DOKUMENTASI TEKNIS: PIPELINE DATA ANALISIS SENTIMEN & PREDIKSI PASAR KRIPTO
**Subjek:** Rekapitulasi Metodologi Pengolahan Data (2021 - 2025)

Dokumen ini merangkum seluruh alur kerja teknis (*data pipeline*) yang telah diimplementasikan dalam pengolahan dataset dari tiga figur publik (Elon Musk, Michael Saylor, Donald Trump) terhadap 10 aset kripto utama.

---

### **PENJELASAN 1: Pengumpulan Data (Raw Data Collection)**
*   **Nama Tahapan:** Akuisisi Data Mentah Media Sosial dan Harga Pasar.
*   **Detail Logika & Codingan:** 
    *   **Data Sosial:** Data ditarik dari platform Twitter dan Truth Social menggunakan teknik *web scraping* (Selenium). Dataset mentah mencakup identitas tweet (`id`), waktu posting (`timestamp`), isi teks (`content`), dan metrik interaksi (`likes`, `retweets`).
    *   **Data Harga:** Data historis per jam (*hourly*) dari 10 ticker (BTC, ETH, SOL, BNB, ADA, XRP, DOGE, TRX, LINK, AVAX) ditarik melalui API bursa (Binance). Setiap file harga memiliki struktur kolom standar: `timestamp`, `open`, `high`, `low`, `close`, dan `volume`.
*   **Output Akhir:** `all_musk_posts.csv`, `saylor_ALL_tweets_RAW.csv`, `trump_ALL_tweets_RAW.csv`, serta 10 file harga seperti `BTCUSDT_1h_prices.csv`.

---

### **PENJELASAN 2: Pra-pemrosesan Data (Text Cleaning & Temporal Sync)**
*   **Nama Tahapan:** Standarisasi Narasi dan Sinkronisasi Waktu.
*   **Detail Logika & Codingan:** 
    *   **Filtering Narasi:** Menggunakan fungsi `df.apply()` untuk memfilter tweet balasan (*replies*) yang diawali karakter `@` agar hanya menyisakan narasi asli figur publik.
    *   **Pembersihan Regex:** Menggunakan library `re` (Regular Expression) untuk menghapus URL (`http\S+`), *mentions* (`@\w+`), emoji, dan karakter khusus lainnya. Tanda baca dasar (`. , ? !`) dipertahankan menggunakan pola `[^a-z0-9\s.,?!]`.
    *   **Normalisasi Teks:** Dilakukan *case folding* (lowercase) dan penggantian karakter *line-break* (`\n`, `\r`, `\t`) menjadi spasi tunggal menggunakan `re.sub(r'\s+', ' ')`.
    *   **Temporal Sync:** Seluruh data sosial digabungkan menggunakan `pd.concat()` dan waktu diseragamkan ke format UTC menggunakan `pd.to_datetime(format='ISO8601', utc=True)`.
*   **Output Akhir:** `merged_social_crypto_2021_2025.csv`

---

### **PENJELASAN 3: Pemetaan Narasi dan Aset (Mapping & Explosion)**
*   **Nama Tahapan:** *Narrative-to-Asset Mapping & Time-Price Synchronization*.
*   **Detail Logika & Codingan:** 
    *   **Keyword Mapping:** Dibuat dictionary pemetaan koin spesifik dan narasi umum (Bitcoin/Crypto/Web3). Jika teks mengandung kata kunci umum, baris tersebut ditandai menargetkan ke-10 ticker koin.
    *   **Explode Logic:** Menggunakan fungsi `df.explode('target_coins')` dari Pandas untuk mentransformasi satu tweet yang menargetkan banyak koin menjadi baris-baris mandiri bagi setiap koin terkait.
    *   **Time Rounding:** Dilakukan pembulatan waktu posting ke jam terdekat menggunakan `dt.floor('h')` untuk menyesuaikan dengan index data harga 1 jam.
    *   **Merge Operation:** Dilakukan `pd.merge()` (inner join) antara data sosial yang sudah di-*explode* dengan dataset harga berdasarkan kolom `timestamp` dan `target_coins`.
*   **Output Akhir:** `MASTER_DATASET_FOR_MODEL.csv`

---

### **PENJELASAN 4: Rekayasa Fitur (Feature Engineering)**
*   **Nama Tahapan:** Kuantifikasi Sentimen, Kategorisasi Narasi, dan Fitur Pasar.
*   **Detail Logika & Codingan:** 
    *   **Kuantifikasi Sentimen:** Menggunakan model **ProsusAI/finbert** melalui library `transformers.pipeline`. Diterapkan **Aturan Ambivalen**: Jika selisih probabilitas label tertinggi dan kedua < 0,15, maka kelas ditetapkan sebagai `neutral`.
    *   **Lexicon Override:** Sentimen dikoreksi menggunakan leksikon kripto (positif: *moon, hodl, bullish*; negatif: *rekt, rug, dump*).
    *   **Kategorisasi Objektif:** Menggunakan *Zero-Shot Classification* (`facebook/bart-large-mnli`) untuk membagi narasi menjadi `Personal`, `Policy-Government`, atau `Policy-Corporate`.
    *   **Fitur Kontekstual:** Menghitung `Price_Runup_24H` menggunakan operasi vektor: `(Price_T0 - Price_Tminus24) / Price_Tminus24`.
    *   **Target Labeling:** Membuat variabel dependen `Tren_Harga_24H` (1 jika `Close_T24 > Close_T0`, else 0).
*   **Output Akhir:** `MASTER_DATASET_FINAL_CATEGORIZED.csv`

---

### **PENJELASAN 5: Penyaringan Peristiwa Makroekonomi (Event Filtering)**
*   **Nama Tahapan:** Eliminasi Noise Eksternal (*Macro-Event Cleaning*).
*   **Detail Logika & Codingan:** 
    *   **Event Windowing:** Dibuat daftar tanggal rilis FOMC dan CPI dari 2021 s.d. 2025.
    *   **Logika Filtering:** Menggunakan fungsi `timedelta(days=1)` untuk membuat jendela waktu **+/- 24 jam** dari setiap event. 
    *   **Dropping:** Baris data yang berada dalam jendela kontaminasi makroekonomi ini dibuang menggunakan *boolean indexing*. Langkah ini krusial untuk memastikan korelasi yang diukur hanya berasal dari narasi figur publik, bukan sentimen makro global.
*   **Output Akhir:** `MASTER_DATASET_FILTERED.csv`

---

### **PENJELASAN 6: Pembagian Dataset & Pre-processing Lanjutan**
*   **Nama Tahapan:** *Temporal Splitting, Encoding,* dan *Feature Scaling*.
*   **Detail Logika & Codingan:** 
    *   **Temporal Split:** Pembagian data dilakukan secara kronologis (bukan random) untuk menghindari *data leakage*. Data sebelum '2025-01-01' dialokasikan sebagai **Train Set** (15.306 baris), dan data Januari 2025 ke atas sebagai **Test Set** (1.290 baris).
    *   **One-Hot Encoding:** Mengonversi kolom kategori menjadi variabel dummy menggunakan `pd.get_dummies(dtype=int)`.
    *   **Feature Scaling:** Menggunakan `StandardScaler` dari `sklearn.preprocessing`. Teknik `fit_transform` hanya dilakukan pada *Train Set*, kemudian parameter rata-rata dan standar deviasi tersebut digunakan untuk me-`transform` *Test Set*. Fitur yang di-scale meliputi `likes`, `retweets`, `prob_pos/neg/neu`, dan `Price_Runup_24H`.
*   **Output Akhir:** `TRAIN_SET_SCALED.csv` dan `TEST_SET_SCALED.csv`

---
**Disusun Oleh:** Gemini CLI Data Pipeline System
**Tanggal Dokumen:** 2026-03-13
