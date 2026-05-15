import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

def build_and_train_lstm():
    print("="*50)
    print("MEMULAI PELATIHAN LONG SHORT-TERM MEMORY (LSTM)")
    print("="*50)

    # Langkah 1: Load Tensor 3D
    try:
        X_train = np.load('27_STAGE6_X_train_3D.npy')
        y_train = np.load('24_LSTM_y_train.npy')
        X_test = np.load('28_STAGE6_X_test_3D.npy')
        y_test = np.load('29_STAGE6_y_test.npy')
    except Exception as e:
        print(f"Gagal memuat dataset .npy: {e}")
        return

    print(f"\n[Data Termuat]")
    print(f"X_train : {X_train.shape} -> (Samples, Timesteps, Features)")
    print(f"X_test  : {X_test.shape} -> (Samples, Timesteps, Features)")

    # Mendapatkan timesteps dan fitur dari shape dataset aktual
    timesteps = X_train.shape[1]
    features = X_train.shape[2]

    # Langkah 2: Membangun Arsitektur Model (Keras Sequential)
    print("\nMembangun arsitektur Sequential LSTM...")
    model = Sequential()
    
    # Input Layer / LSTM Layer 1 (64 unit neuron)
    model.add(LSTM(64, input_shape=(timesteps, features)))
    
    # Regularization Layer (Dropout 20%) untuk kompensasi overfitting
    model.add(Dropout(0.2))
    
    # Dense Layer (Hidden) dengan 32 neuron dan ReLU
    model.add(Dense(32, activation='relu'))
    
    # Output Layer dengan aktivasi Sigmoid untuk probabilitas (0 hingga 1)
    model.add(Dense(1, activation='sigmoid'))
    
    model.summary()

    # Langkah 3: Kompilasi Model
    print("\nMengkompilasi model... (Optimizer: Adam, Loss: Binary Crossentropy)")
    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    # Langkah 4: Konfigurasi Early Stopping
    early_stopping = EarlyStopping(
        monitor='val_loss', 
        patience=10, 
        restore_best_weights=True,
        verbose=1
    )

    # Langkah 5: Training (Proses Fitting)
    print("\n[FIT] Memulai proses training (Max Epochs: 100, Batch Size: 32)...")
    history = model.fit(
        X_train, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping],
        verbose=1
    )

    # Langkah 6: Ekspor Model & History Plot
    model_name = '30_STAGE6_MODEL_Final_LSTM.keras'
    model.save(model_name)
    print(f"\n[SUKSES] Model Keras telah diekspor dan disimpan sebagai: {model_name}")

    # Plot grafik pergerakan loss dan val_loss
    try:
        print("\nMembuat visualisasi konvergensi Loss Epoch...")
        plt.figure(figsize=(10, 6))
        plt.plot(history.history['loss'], label='Training Loss', color='blue')
        plt.plot(history.history['val_loss'], label='Validation Loss', color='red', linestyle='--')
        plt.title('Kurva Pembelajaran (Learning Curve) - Penurunan Loss', fontweight='bold')
        plt.xlabel('Epochs')
        plt.ylabel('Binary Crossentropy Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plot_filename = 'lstm_learning_curve.png'
        plt.savefig(plot_filename)
        print(f"[SUKSES] Grafik pembelajaran berhasil diekspor sebagai: {plot_filename}")
    except Exception as e:
        print(f"[ERROR] Gagal membuat plot: {e}")

if __name__ == "__main__":
    build_and_train_lstm()



