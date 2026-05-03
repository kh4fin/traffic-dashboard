import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os


import sqlite3

def load_data(filepath):
    if filepath.endswith('.db'):
        # Baca dari SQLite
        conn = sqlite3.connect(filepath)
        df = pd.read_sql_query("SELECT * FROM traffic_data", conn)
        conn.close()
    else:
        # Baca dari CSV (Data Dummy)
        df = pd.read_csv(filepath)
        
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    df = df.dropna()
    return df


def create_sequences(data, window_size=20):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:(i + window_size)])
        y.append(data[i + window_size])
    return np.array(X), np.array(y)


def preprocess_multifeature(filepath, location=None, window_size=20, test_size=0.05):
    df = load_data(filepath)
    
    # Filter berdasarkan lokasi jika ditentukan
    if location:
        df = df[df['lokasi'] == location].copy()
    
    values = df['jumlah_kendaraan'].values.reshape(-1, 1)

    scaler_y = MinMaxScaler()
    scaled_y = scaler_y.fit_transform(values).flatten()

    df['hour'] = df['timestamp'].dt.hour
    
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['day_sin'] = np.sin(2 * np.pi * df['hari'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['hari'] / 7)
    
    df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9) | (df['hour'] >= 16) & (df['hour'] <= 19)).astype(float)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(float)

    feature_scaler = StandardScaler()
    features_list = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'is_rush_hour', 'is_night', 'is_weekend']
    features = df[features_list].values
    scaled_features = feature_scaler.fit_transform(features)

    main_seq, y = create_sequences(scaled_y, window_size)
    feat_seq = []
    for i in range(len(scaled_features) - window_size):
        feat_seq.append(scaled_features[i:(i + window_size)])
    feat_seq = np.array(feat_seq)

    X = np.concatenate([main_seq.reshape(-1, window_size, 1), feat_seq], axis=-1)

    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(indices, test_size=test_size, random_state=42)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    return X_train, X_test, y_train, y_test, scaler_y


def get_latest_window(filepath, location=None, window_size=20):
    """Mengambil window data terakhir untuk input prediksi real-time"""
    df = load_data(filepath)
    if location:
        df = df[df['lokasi'] == location].copy()
    
    if len(df) < window_size:
        return None, None

    # Proses persis seperti preprocessing utama
    values = df['jumlah_kendaraan'].values.reshape(-1, 1)
    scaler_y = MinMaxScaler()
    scaled_y = scaler_y.fit_transform(values).flatten()

    df['hour'] = df['timestamp'].dt.hour
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['hari'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['hari'] / 7)
    df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9) | (df['hour'] >= 16) & (df['hour'] <= 19)).astype(float)
    df['is_night'] = ((df['hour'] >= 22) | (df['hour'] <= 5)).astype(float)

    features_list = ['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'is_rush_hour', 'is_night', 'is_weekend']
    feature_scaler = StandardScaler()
    scaled_features = feature_scaler.fit_transform(df[features_list].values)

    # Ambil window terakhir
    last_y_seq = scaled_y[-window_size:]
    last_feat_seq = scaled_features[-window_size:]
    
    X = np.concatenate([last_y_seq.reshape(1, window_size, 1), last_feat_seq.reshape(1, window_size, -1)], axis=-1)
    
    return X, scaler_y


def save_scaler(scaler, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(scaler, f)


def load_scaler(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)


if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "traffic.csv")
    X_train, X_test, y_train, y_test, scaler = preprocess_multifeature(data_path, window_size=20, test_size=0.05)
    print(f"Train shape: X={X_train.shape}, y={y_train.shape}")
    print(f"Test shape: X={X_test.shape}, y={y_test.shape}")    