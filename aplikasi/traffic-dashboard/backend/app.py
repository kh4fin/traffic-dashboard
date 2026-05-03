from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import os
import sys

SCAFFOLD_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SCAFFOLD_DIR)

from preprocessing.preprocessing import preprocess_multifeature, load_scaler
from evaluation.metrics import evaluate

app = Flask(__name__)
CORS(app)

# Data dummy sebagai pondasi (untuk history & metrics)
DATA_PATH = os.path.join(SCAFFOLD_DIR, "data", "traffic.csv")
# Database asli dari detektor (untuk input ramalan real-time)
DB_REAL_PATH = os.path.join(SCAFFOLD_DIR, "deteksi", "traffic.db")
MODEL_PATH = os.path.join(SCAFFOLD_DIR, "saved_model", "model.keras")
SCALER_PATH = os.path.join(SCAFFOLD_DIR, "saved_model", "scaler.pkl")
FRONTEND_DIR = os.path.join(SCAFFOLD_DIR, "frontend")

X_train, X_test, y_train, y_test, scaler = None, None, None, None, None
model = None
metrics_cache = None


def load_model():
    global model, X_train, X_test, y_train, y_test, scaler, metrics_cache
    if model is None:
        X_train, X_test, y_train, y_test, scaler = preprocess_multifeature(
            DATA_PATH, window_size=20, test_size=0.2
        )
        scaler = load_scaler(SCALER_PATH)
        from tensorflow.keras.models import load_model as keras_load
        model = keras_load(MODEL_PATH)
        y_pred_scaled = model.predict(X_test, verbose=0).flatten()
        y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        y_true = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        metrics_cache = evaluate(y_true, y_pred)


@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)


@app.route('/api/data', methods=['GET'])
def get_data():
    import pandas as pd
    df = pd.read_csv(DATA_PATH)
    data = df.to_dict(orient='records')
    return jsonify({"data": data, "count": len(data)})


def get_traffic_status(count):
    if count <= 50:
        return {
            "status": "Lancar",
            "color": "#10b981", # Emerald Green
            "message": "Jalanan sangat lega. Waktu yang tepat untuk berangkat!",
            "icon": "bi-check-circle"
        }
    elif count <= 130:
        return {
            "status": "Ramai Lancar",
            "color": "#f59e0b", # Amber/Orange
            "message": "Lalu lintas mulai berisi. Tetap waspada di jalan.",
            "icon": "bi-info-circle"
        }
    else:
        return {
            "status": "Padat",
            "color": "#ef4444", # Red
            "message": "Terjadi kepadatan kendaraan. Harap cari rute alternatif jika memungkinkan.",
            "icon": "bi-exclamation-triangle"
        }


@app.route('/api/predict', methods=['GET'])
def get_predict():
    from flask import request
    lokasi = request.args.get('location', 'Simpang_A')
    
    load_model()
    
    # STRATEGI HYBRID:
    # 1. Cek apakah ada data asli dari CCTV di SQLite untuk lokasi ini
    X_input = None
    scaler_input = None
    
    if os.path.exists(DB_REAL_PATH):
        from preprocessing.preprocessing import get_latest_window
        X_input, scaler_input = get_latest_window(DB_REAL_PATH, location=lokasi, window_size=20)
    
    # 2. Jika data asli belum cukup (misal belum 10 menit jalan), gunakan data dummy (CSV)
    if X_input is None:
        print(f"Menggunakan data dummy untuk ramalan {lokasi}...")
        _, X_dummy, _, _, scaler_dummy = preprocess_multifeature(
            DATA_PATH, location=lokasi if lokasi == 'Simpang_A' else 'Simpang_A', window_size=20, test_size=0.2
        )
        X_input = X_dummy
        scaler_input = scaler_dummy
    else:
        print(f"MENGGUNAKAN DATA ASLI CCTV untuk ramalan {lokasi}!")

    # Prediksi menggunakan input yang terpilih (Asli atau Dummy)
    y_pred_scaled = model.predict(X_input, verbose=0).flatten()
    y_pred = scaler_input.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
    
    # Untuk data aktual (actual), kita tetap ambil dari data pondasi agar grafik tidak kosong
    _, X_base, _, y_test_base, scaler_base = preprocess_multifeature(
        DATA_PATH, location='Simpang_A', window_size=20, test_size=0.2
    )
    y_true = scaler_base.inverse_transform(y_test_base.reshape(-1, 1)).flatten()
    
    # Ambil prediksi terbaru
    latest_pred = float(y_pred[-1])
    status_info = get_traffic_status(latest_pred)
    
    # Ambil ramalan 5 jam ke depan (sebagai contoh simulasi)
    forecast = []
    for i in range(1, 6):
        if i < len(y_pred):
            val = float(y_pred[-i])
            forecast.append({
                "time": f"+{i} Jam",
                "value": round(val),
                "status": get_traffic_status(val)["status"]
            })

    return jsonify({
        "actual": y_true.tolist(),
        "predicted": y_pred.tolist(),
        "latest": {
            "value": round(latest_pred),
            **status_info
        },
        "forecast": forecast
    })


@app.route('/api/evaluate', methods=['GET'])
def get_evaluate():
    load_model()
    # Kita tetap kirim metrics untuk dev, tapi dashboard utama tidak perlu menampilkannya
    return jsonify(metrics_cache)


if __name__ == '__main__':
    app.run(debug=True, port=5000)