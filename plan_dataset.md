# PLAN: Dataset Generator untuk Traffic Time-Series

## 🎯 OBJECTIVE

Membuat dataset time-series jumlah kendaraan secara otomatis (dummy/simulasi) untuk digunakan pada model LSTM.

Dataset harus menyerupai pola lalu lintas nyata:

- Jam sibuk (pagi & sore)
- Jam sepi (malam)
- Fluktuatif (tidak linear)

---

## 📂 OUTPUT

File CSV:
traffic_generated.csv

Format:
timestamp,jumlah_kendaraan

---

## 🧱 STRATEGI GENERASI DATA

Gunakan pendekatan:

1. Time-based pattern (jam)
2. Random noise
3. Peak simulation (rush hour)

---

## ⏱️ STEP 1: GENERATE TIMESTAMP

- Interval: 1 menit
- Durasi: minimal 3–7 hari
- Format: YYYY-MM-DD HH:MM

Contoh:
2025-01-01 00:00
2025-01-01 00:01
...

---

## 📈 STEP 2: DEFINE TRAFFIC PATTERN

Gunakan aturan:

- 00:00–05:00 → sangat sepi (0–10 kendaraan)
- 06:00–09:00 → jam sibuk pagi (50–150 kendaraan)
- 10:00–15:00 → normal (30–80 kendaraan)
- 16:00–19:00 → jam sibuk sore (80–180 kendaraan)
- 20:00–23:00 → menurun (10–40 kendaraan)

---

## 🎲 STEP 3: ADD RANDOMNESS

Tambahkan variasi:

- random.uniform / random.randint
- noise ±10–20%

Tujuan:

- data tidak terlalu “rapi”
- lebih realistis

---

## 📉 STEP 4: SIMULATE FLUCTUATION

Tambahkan:

- naik turun kecil antar menit
- hindari angka konstan

---

## 💾 STEP 5: SAVE CSV

Kolom:
timestamp,jumlah_kendaraan

---

## 🧪 STEP 6: VALIDATION

Pastikan:

- tidak ada nilai negatif
- tidak ada missing value
- pola terlihat (pagi & sore tinggi)

---

## 🚀 OPTIONAL IMPROVEMENTS

- Tambahkan hari (weekday/weekend)
- Weekend lebih sepi
- Tambahkan event spike (misal lonjakan tiba-tiba)

---

## 📊 EXPECTED RESULT

Dataset:

- realistis
- memiliki pola time-series
- siap untuk LSTM training
