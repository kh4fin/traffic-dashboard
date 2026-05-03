import os
import subprocess
import time
from datetime import datetime

# --- KONFIGURASI VPS ANDA ---
VPS_IP = "159.223.xx.xx"  # Ganti dengan IP VPS Anda
VPS_USER = "root"
REMOTE_PATH = "/root/traffic.db"  # Lokasi file db di VPS
LOCAL_PATH = "./traffic_backup.db"  # Nama file setelah di-download ke laptop
SYNC_INTERVAL = 3600  # Sinkronisasi setiap 1 jam (3600 detik)
# ----------------------------

def sync_data():
    print(f"[{datetime.now()}] Memulai sinkronisasi dari VPS...")
    
    # Perintah SCP untuk download file
    # Format: scp user@ip:remote_path local_path
    scp_command = f"scp {VPS_USER}@{VPS_IP}:{REMOTE_PATH} {LOCAL_PATH}"
    
    try:
        # Menjalankan perintah terminal
        result = subprocess.run(scp_command, shell=True, check=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] BERHASIL: Data telah dicadangkan ke {LOCAL_PATH}")
        else:
            print(f"[{datetime.now()}] GAGAL: Terjadi kesalahan saat menyalin data.")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR: Pastikan SSH Key sudah terpasang atau password benar. \nDetail: {e}")

if __name__ == "__main__":
    print("Sistem Auto-Sync Aktif. Menekan CTRL+C untuk berhenti.")
    while True:
        sync_data()
        print(f"Menunggu {SYNC_INTERVAL//60} menit untuk sinkronisasi berikutnya...")
        time.sleep(SYNC_INTERVAL)
