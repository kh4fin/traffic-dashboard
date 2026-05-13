import os
import sqlite3
import time
from datetime import datetime

# --- KONFIGURASI ---
SOURCE_DB = "traffic.db"         # Database hasil deteksi laptop
MASTER_DB = "master_traffic.db"  # Database utama untuk dashboard
SYNC_INTERVAL = 60               # Cek penggabungan setiap 1 menit
# --------------------

def init_master_db():
    """Memastikan database master siap menerima data"""
    conn = sqlite3.connect(MASTER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            lokasi TEXT,
            hari INTEGER,
            is_weekend INTEGER,
            jumlah_kendaraan INTEGER,
            UNIQUE(timestamp, lokasi)
        )
    ''')
    conn.commit()
    conn.close()

def merge_local_to_master():
    if not os.path.exists(SOURCE_DB):
        print(f"[{datetime.now()}] Menunggu file {SOURCE_DB} dibuat oleh detektor...")
        return

    print(f"[{datetime.now()}] Menggabungkan data lokal ke master...")
    
    try:
        master_conn = sqlite3.connect(MASTER_DB)
        master_cursor = master_conn.cursor()

        # Lampirkan source_db agar bisa akses tabelnya
        master_cursor.execute(f"ATTACH DATABASE '{SOURCE_DB}' AS local_source")

        # Pindahkan data unik
        master_cursor.execute('''
            INSERT OR IGNORE INTO traffic_data (timestamp, lokasi, hari, is_weekend, jumlah_kendaraan)
            SELECT timestamp, lokasi, hari, is_weekend, jumlah_kendaraan FROM local_source.traffic_data
        ''')
        
        inserted_rows = master_cursor.rowcount
        master_conn.commit()
        
        # Lepaskan lampiran
        master_cursor.execute("DETACH DATABASE local_source")
        master_conn.close()

        print(f"[{datetime.now()}] BERHASIL: {inserted_rows} data baru digabungkan ke {MASTER_DB}")
        
    except Exception as e:
        print(f"[{datetime.now()}] ERROR saat merge: {e}")

if __name__ == "__main__":
    init_master_db()
    print("=========================================")
    print("SISTEM SINKRONISASI LOKAL AKTIF")
    print(f"Source: {SOURCE_DB} -> Target: {MASTER_DB}")
    print("Tekan CTRL+C untuk berhenti")
    print("=========================================")
    
    while True:
        try:
            merge_local_to_master()
        except KeyboardInterrupt:
            print("Berhenti.")
            break
        except Exception as e:
            print(f"Error utama: {e}")
            
        time.sleep(SYNC_INTERVAL)
