# ==============================================================================
#           SKRIP LENGKAP CEK KONEKSI INTERNET & NOTIFIKASI WINDOWS
#             (Versi Notifikasi Berulang Saat Offline)
# ==============================================================================

# --- 1. Import Library ---
import socket
import time
import os
import datetime
from winotify import Notification

# --- 2. Konfigurasi ---
HOST_TERPERCAYA = "8.8.8.8"
PORT_TERPERCAYA = 53
INTERVAL_CEK = 15                   # Interval pengecekan normal (detik)
INTERVAL_CEK_OFFLINE = 10           # Interval pengecekan saat offline (detik)
NAMA_IKON_ONLINE = "router.ico"       # Ikon untuk status online
NAMA_IKON_OFFLINE = "error-404.ico" # Ikon untuk status offline

# --- 3. Penentuan Path Ikon (Hanya dijalankan sekali) ---
direktori_skrip = os.path.dirname(os.path.abspath(__file__))

# Cari path untuk ikon ONLINE
path_ikon_online_lengkap = os.path.join(direktori_skrip, NAMA_IKON_ONLINE)
if os.path.exists(path_ikon_online_lengkap):
    ICON_PATH_ONLINE = path_ikon_online_lengkap
else:
    # Fallback jika ikon online tidak ada: ikon "Info" Windows
    ICON_PATH_ONLINE = r"C:\Windows\System32\shell32.dll,-24" 
    print(f"PERINGATAN: File ikon '{NAMA_IKON_ONLINE}' tidak ditemukan.")

# Cari path untuk ikon OFFLINE
path_ikon_offline_lengkap = os.path.join(direktori_skrip, NAMA_IKON_OFFLINE)
if os.path.exists(path_ikon_offline_lengkap):
    ICON_PATH_OFFLINE = path_ikon_offline_lengkap
else:
    # Fallback jika ikon offline tidak ada: ikon "Error" Windows
    ICON_PATH_OFFLINE = r"C:\Windows\System32\shell32.dll,-23" 
    print(f"PERINGATAN: File ikon '{NAMA_IKON_OFFLINE}' tidak ditemukan.")

# --- 4. Definisi Fungsi ---
def cek_koneksi():
    """Mencoba membuat koneksi socket. Mengembalikan True jika berhasil, False jika gagal."""
    try:
        socket.create_connection((HOST_TERPERCAYA, PORT_TERPERCAYA), timeout=3)
        return True
    except (socket.timeout, OSError):
        return False

def kirim_notifikasi(status_online: bool, pesan_awal=False):
    """Membuat dan mengirim notifikasi dengan ikon yang sesuai status."""
    try:
        # Tentukan ikon yang akan digunakan berdasarkan status
        ikon_pilihan = ICON_PATH_ONLINE if status_online else ICON_PATH_OFFLINE

        # Tentukan judul dan pesan notifikasi
        if pesan_awal:
            judul = "Monitoring Dimulai"
            pesan = f"Status koneksi awal: {'NORMAL' if status_online else 'TERPUTUS'}"
        elif status_online:
            judul = "Koneksi Internet Kembali Normal"
            pesan = f"Terhubung kembali pada {datetime.datetime.now().strftime('%H:%M:%S')}."
        else:
            judul = "Koneksi Internet Terputus!"
            pesan = f"Mencoba menyambung kembali... (dicek tiap {INTERVAL_CEK_OFFLINE} detik)"

        # Buat objek notifikasi dengan ikon yang sudah dipilih
        notifikasi = Notification(
            app_id="Monitoring Internet",
            title=judul,
            msg=pesan,
            icon=ikon_pilihan
        )
        notifikasi.show()
    except Exception as e:
        print("\n--- !!! GAGAL MENGIRIM NOTIFIKASI !!! ---")
        print(f"Error: {e}")

# --- 5. Program Utama (Logika Diubah) ---
if __name__ == "__main__":
    print("🖥️  Memulai skrip pemantauan koneksi internet...")
    print("(Tekan CTRL+C untuk menghentikan.)")
    
    print("\nMelakukan pengecekan awal...")
    status_terakhir = cek_koneksi()
    kirim_notifikasi(status_online=status_terakhir, pesan_awal=True)
    
    status_text = "NORMAL" if status_terakhir else "TERPUTUS"
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status awal koneksi: {status_text}")

    while True:
        try:
            status_sekarang = cek_koneksi()
            
            # --- LOGIKA BARU ---
            
            # KONDISI 1: Koneksi TERPUTUS (baik baru saja atau sudah dari tadi)
            if not status_sekarang:
                # Jika status baru saja berubah jadi offline, cetak header perubahan
                if status_sekarang != status_terakhir:
                    print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Perubahan status terdeteksi!")
                
                # Kirim notifikasi berulang kali (CMD dan Windows)
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status baru: TERPUTUS")
                kirim_notifikasi(status_online=False)
                
                # Update status dan tunggu interval pendek
                status_terakhir = status_sekarang
                time.sleep(INTERVAL_CEK_OFFLINE)

            # KONDISI 2: Koneksi BARU SAJA KEMBALI NORMAL
            elif status_sekarang and not status_terakhir:
                print(f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Perubahan status terdeteksi!")
                print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Status baru: NORMAL")
                kirim_notifikasi(status_online=True)
                
                # Update status dan tunggu interval normal
                status_terakhir = status_sekarang
                time.sleep(INTERVAL_CEK)
            
            # KONDISI 3: Koneksi tetap NORMAL (tidak ada notifikasi, hanya menunggu)
            else:
                status_terakhir = status_sekarang
                time.sleep(INTERVAL_CEK)

        except KeyboardInterrupt:
            print("\nSkrip dihentikan oleh pengguna. Sampai Jumpa!")
            break