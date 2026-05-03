# PROJECT PLAN: Traffic Analysis Dashboard (LSTM-Based)

## 🎯 OBJECTIVE

Membangun sistem dashboard berbasis web untuk menganalisis pola lalu lintas menggunakan data time-series jumlah kendaraan dan model LSTM.

---

## 🧱 SYSTEM ARCHITECTURE

Data (CSV)
→ Preprocessing
→ LSTM Model
→ Evaluation (MAE, RMSE, MAPE)
→ Backend API (Flask)
→ Frontend Dashboard (Chart.js)

---

## 📂 PROJECT STRUCTURE

traffic-dashboard/
│
├── data/
│ └── traffic.csv
│
├── preprocessing/
│ └── preprocessing.py
│
├── model/
│ └── lstm_model.py
│
├── evaluation/
│ └── metrics.py
│
├── backend/
│ └── app.py
│
├── frontend/
│ ├── index.html
│ ├── style.css
│ └── script.js
│
├── saved_model/
│ └── model.h5
│
└── notebooks/
└── experiment.ipynb

---

## 📅 DEVELOPMENT PHASES

### Phase 1: Data Preparation

- Load CSV dataset
- Validate format (timestamp, jumlah_kendaraan)
- Handle missing values
- Sort by timestamp

### Phase 2: Preprocessing

- Normalize data using MinMaxScaler
- Convert data into sequences (window size: 10–20)
- Split into train/test (80/20)

### Phase 3: Model Training (LSTM)

- Build LSTM model:
  - 2 LSTM layers
  - Dense output layer
- Compile with Adam optimizer & MSE loss
- Train model (epochs: 20–50)
- Save trained model

### Phase 4: Prediction

- Load trained model
- Predict on test data
- Inverse transform prediction

### Phase 5: Evaluation

- Calculate:
  - MAE
  - RMSE
  - MAPE
- Store results in JSON

### Phase 6: Backend API (Flask)

Create endpoints:

- /api/data → return raw data
- /api/predict → return prediction
- /api/evaluate → return metrics

### Phase 7: Frontend Dashboard

- Display:
  - Line chart (actual vs prediction)
  - Evaluation metrics
- Use Chart.js

---

## 📊 OUTPUT EXPECTED

- Grafik tren kendaraan
- Grafik prediksi vs actual
- Nilai MAE, RMSE, MAPE

---

## ⚠️ CONSTRAINTS

- Data bersifat time-series
- Model utama: LSTM
- Tidak melakukan deteksi kendaraan (hanya analisis)

---

## 🚀 FUTURE IMPROVEMENTS (OPTIONAL)

- Compare with baseline model (Linear Regression)
- Add real-time simulation
- Add multi-location support
