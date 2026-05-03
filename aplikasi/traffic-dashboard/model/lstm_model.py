import os
import sys
import numpy as np
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (LSTM, Dense, Dropout, Layer, 
                               Bidirectional, Input, Conv1D, MaxPooling1D,
                               GlobalAveragePooling1D, BatchNormalization)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.preprocessing import preprocess_multifeature
from evaluation.metrics import evaluate

SCAFFOLD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_cnn_lstm(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        
        Conv1D(64, 3, activation='relu', padding='same'),
        Conv1D(64, 3, activation='relu', padding='same'),
        MaxPooling1D(2),
        Dropout(0.2),
        
        Bidirectional(LSTM(128, return_sequences=True)),
        Dropout(0.2),
        
        Bidirectional(LSTM(64, return_sequences=True)),
        Dropout(0.2),
        
        GlobalAveragePooling1D(),
        
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(32, activation='relu'),
        Dense(1)
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    return model


def train_model(X_train, y_train, epochs=200, batch_size=16, verbose=1):
    model = build_cnn_lstm((X_train.shape[1], X_train.shape[2]))
    
    early_stop = EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=8, min_lr=0.00001, verbose=1)
    
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.15,
        callbacks=[early_stop, reduce_lr],
        verbose=verbose
    )
    
    return model, history


def predict(model, X_test):
    return model.predict(X_test, verbose=0).flatten()


if __name__ == "__main__":
    data_path = os.path.join(SCAFFOLD_DIR, "data", "traffic.csv")
    model_path = os.path.join(SCAFFOLD_DIR, "saved_model", "model.keras")
    scaler_path = os.path.join(SCAFFOLD_DIR, "saved_model", "scaler.pkl")
    
    window_size = 20
    test_size = 0.1
    lokasi_target = "Simpang_A" # Kita bisa ubah ini untuk training lokasi lain
    
    print(f"Loading data for {lokasi_target} with feature engineering (10% test)...")
    X_train, X_test, y_train, y_test, scaler = preprocess_multifeature(
        data_path, location=lokasi_target, window_size=window_size, test_size=test_size
    )
    print(f"Train: {X_train.shape}, Test: {X_test.shape}")
    
    print(f"\nTraining CNN-BiLSTM model (epochs=200, batch_size=16, test=10%)...")
    model, history = train_model(X_train, y_train, epochs=200, batch_size=16)
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    
    from preprocessing.preprocessing import save_scaler
    save_scaler(scaler, scaler_path)
    print(f"\nModel saved to {model_path}")
    
    y_pred_scaled = predict(model, X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    y_true = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
    
    metrics = evaluate(y_true, y_pred)
    print(f"\nMetrics - MAE: {metrics['MAE']:.2f}, RMSE: {metrics['RMSE']:.2f}, MAPE: {metrics['MAPE']:.2f}%")
    
    if metrics['MAPE'] < 10:
        print("\nTARGET MAPE < 10% TERCAPAI!")