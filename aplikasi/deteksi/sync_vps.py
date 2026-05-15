import os
import subprocess
import sqlite3
import time
from datetime import datetime



VPS_IP = "167.99.71.227"
VPS_USER = "root"

REMOTE_DB = "/root/traffic.db"

REMOTE_BACKUP_DB = "/root/traffic_backup.db"

LOCAL_MASTER_DB = "master_traffic.db"

TEMP_DB = "traffic_temp.db"

SYNC_INTERVAL = 300


def init_db():
    conn = sqlite3.connect(LOCAL_MASTER_DB)
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


def create_remote_backup():
    print(f"[{datetime.now()}] Membuat backup database di VPS...")

    backup_command = (
        f"ssh {VPS_USER}@{VPS_IP} "
        f"\"sqlite3 {REMOTE_DB} '.backup {REMOTE_BACKUP_DB}'\""
    )

    try:
        result = subprocess.run(
            backup_command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("GAGAL membuat backup di VPS")
            print(result.stderr)
            return False

        print("Backup VPS berhasil dibuat")
        return True

    except Exception as e:
        print(f"ERROR saat membuat backup VPS: {e}")
        return False


def download_backup():
    print(f"[{datetime.now()}] Download database backup dari VPS...")

    scp_command = (
        f"scp {VPS_USER}@{VPS_IP}:{REMOTE_BACKUP_DB} {TEMP_DB}"
    )

    try:
        result = subprocess.run(
            scp_command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("GAGAL download database")
            print(result.stderr)
            return False

        if not os.path.exists(TEMP_DB):
            print("File hasil download tidak ditemukan")
            return False

        file_size = os.path.getsize(TEMP_DB)

        print(f"Download berhasil ({file_size} bytes)")

        if file_size == 0:
            print("Database hasil download kosong")
            return False

        return True

    except Exception as e:
        print(f"ERROR saat download: {e}")
        return False


def merge_databases():

    if not os.path.exists(TEMP_DB):
        print("TEMP_DB tidak ditemukan")
        return

    print(f"[{datetime.now()}] Menggabungkan database...")

    try:
        master_conn = sqlite3.connect(LOCAL_MASTER_DB)
        master_cursor = master_conn.cursor()

        master_cursor.execute(
            f"ATTACH DATABASE '{TEMP_DB}' AS incoming"
        )

        master_cursor.execute('''
            INSERT OR IGNORE INTO traffic_data
            (
                timestamp,
                lokasi,
                hari,
                is_weekend,
                jumlah_kendaraan
            )
            SELECT
                timestamp,
                lokasi,
                hari,
                is_weekend,
                jumlah_kendaraan
            FROM incoming.traffic_data
        ''')

        inserted_rows = master_cursor.rowcount

        master_conn.commit()

        master_cursor.execute("DETACH DATABASE incoming")

        master_conn.commit()
        master_conn.close()

        os.remove(TEMP_DB)

        print(f"Merge berhasil ({inserted_rows} data baru)")

    except Exception as e:
        print(f"ERROR saat merge database: {e}")


def sync_data():

    print("\n==================================================")
    print(f"[{datetime.now()}] MEMULAI SINKRONISASI")
    print("==================================================")

    backup_ok = create_remote_backup()

    if not backup_ok:
        return

    download_ok = download_backup()

    if not download_ok:
        return

    merge_databases()

    print("Sinkronisasi selesai")


if __name__ == "__main__":

    init_db()

    print("===================================")
    print("SISTEM AUTO MERGE-SYNC AKTIF")
    print("Tekan CTRL+C untuk berhenti")
    print("===================================")

    while True:

        try:
            sync_data()

        except KeyboardInterrupt:
            print("Program dihentikan")
            break

        except Exception as e:
            print(f"ERROR UTAMA: {e}")

        print(f"\nMenunggu {SYNC_INTERVAL // 60} menit...")
        time.sleep(SYNC_INTERVAL)