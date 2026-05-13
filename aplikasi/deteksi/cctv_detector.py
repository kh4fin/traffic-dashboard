import cv2
import time
import sqlite3
import os
from datetime import datetime
from ultralytics import YOLO

CCTV_SOURCES = [
    {"nama": "Semampir", "url": "https://pplterpadu.kedirikota.go.id:8888/semampir/stream.m3u8"},
    {"nama": "Water Torn", "url": "https://pplterpadu.kedirikota.go.id:8888/water_torn/stream.m3u8"},
    {"nama": "A Yani Utara", "url": "https://pplterpadu.kedirikota.go.id:8888/a_yani_utara/stream.m3u8"},
    {"nama": "Jetis", "url": "https://pplterpadu.kedirikota.go.id:8888/jetis/stream.m3u8"},
    {"nama": "Dandangan", "url": "https://pplterpadu.kedirikota.go.id:8888/dandangan/stream.m3u8"},
    {"nama": "Nabatiasa", "url": "https://pplterpadu.kedirikota.go.id:8888/nabatiasa/stream.m3u8"}
]
MODEL_PATH = "yolo11n.pt"  
DB_PATH = "traffic.db" 
INTERVAL_SECONDS = 60  

def init_db():
    # Inisialisasi database SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            lokasi TEXT,
            hari INTEGER,
            is_weekend INTEGER,
            jumlah_kendaraan INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def run_detector():
    print(f"[{datetime.now()}] Memuat model YOLOv11...")
    model = YOLO(MODEL_PATH)
    init_db()
    
    while True:
        start_time = time.time()
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        hari_ke = now.weekday()
        is_weekend = 1 if hari_ke >= 5 else 0

        print(f"\n--- Siklus Deteksi: {timestamp} ---")

        # Hubungkan ke DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for cctv in CCTV_SOURCES:
            try:
                print(f"Memeriksa {cctv['nama']}...", end=" ", flush=True)
                cap = cv2.VideoCapture(cctv['url'])
                if not cap.isOpened():
                    print("GAGAL (URL tidak dapat dibuka)")
                    continue

                ret, frame = cap.read()
                cap.release()

                if not ret:
                    print("GAGAL (Gagal ambil gambar)")
                    continue

                results = model(frame, classes=[2, 3, 5, 7], verbose=False, device='cpu')
                count = len(results[0].boxes)

                # Simpan ke SQLite
                cursor.execute('''
                    INSERT INTO traffic_data (timestamp, lokasi, hari, is_weekend, jumlah_kendaraan)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, cctv['nama'], hari_ke, is_weekend, count))
                
                print(f"BERHASIL ({count} kendaraan)")

            except Exception as e:
                print(f"ERROR pada {cctv['nama']}: {e}")

        conn.commit()
        conn.close()

        elapsed = time.time() - start_time
        wait_time = max(1, INTERVAL_SECONDS - elapsed)
        time.sleep(wait_time)

if __name__ == "__main__":
    run_detector()
