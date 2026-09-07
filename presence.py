import os
import time
from datetime import datetime
from dotenv import load_dotenv
from pypresence import Presence

# Memuat environment variables dari file .env
load_dotenv()

# ==================== KONFIGURASI RICH PRESENCE ====================
CLIENT_ID = os.getenv("PRESENCE_CLIENT_ID", "")

# Detail status yang akan ditampilkan
DETAILS = os.getenv("PRESENCE_DETAILS", "Commanding Luna: Oblivion")
STATE = os.getenv("PRESENCE_STATE", "Void Attribut DPS")

# Gambar Utama & Teks Hover
LARGE_IMAGE = os.getenv("PRESENCE_LARGE_IMAGE", "https://i.imgur.com/TjUb7Gn.gif")
LARGE_TEXT = os.getenv("PRESENCE_LARGE_TEXT", "Luna: Oblivion (Void Class)")

# Gambar Kecil & Teks Hover
SMALL_IMAGE = os.getenv("PRESENCE_SMALL_IMAGE", "")
SMALL_TEXT = os.getenv("PRESENCE_SMALL_TEXT", "Punishing: Gray Raven")

# Waktu Mulai & Selesai (Format: YYYY-MM-DD HH:MM:SS)
START_OFFSET = int(os.getenv("PRESENCE_START_OFFSET", "0"))
START_DATETIME = os.getenv("PRESENCE_START_DATETIME", "")
END_DATETIME = os.getenv("PRESENCE_END_DATETIME", "")

# Squad/Party Settings
PARTY_SIZE = os.getenv("PRESENCE_PARTY_SIZE", "")
PARTY_MAX = os.getenv("PRESENCE_PARTY_MAX", "")
PARTY_ID = os.getenv("PRESENCE_PARTY_ID", "")
JOIN_SECRET = os.getenv("PRESENCE_JOIN_SECRET", "")

# Tombol 1 & 2
BUTTON_LABEL_1 = os.getenv("PRESENCE_BUTTON_LABEL_1", "")
BUTTON_URL_1 = os.getenv("PRESENCE_BUTTON_URL_1", "")
BUTTON_LABEL_2 = os.getenv("PRESENCE_BUTTON_LABEL_2", "")
BUTTON_URL_2 = os.getenv("PRESENCE_BUTTON_URL_2", "")
# ===================================================================

def start_presence():
    if not CLIENT_ID:
        print("❌ ERROR: Harap masukkan CLIENT_ID di file .env Anda!")
        return

    print(f"🔄 Menghubungkan ke Discord Desktop...")
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        print("✅ Terhubung ke Discord Desktop!")

        # Menghitung waktu mulai (start_time)
        start_time = None
        if START_DATETIME:
            try:
                dt = datetime.strptime(START_DATETIME, "%Y-%m-%d %H:%M:%S")
                start_time = int(dt.timestamp())
                print(f"📅 Menggunakan tanggal mulai konstan: {START_DATETIME}")
            except Exception as e:
                print(f"⚠️ Format PRESENCE_START_DATETIME salah ({e}). Menggunakan waktu lokal saat ini.")
                start_time = int(time.time())
        else:
            start_time = int(time.time()) - START_OFFSET if START_OFFSET >= 0 else None

        # Menghitung waktu selesai (end_time) - opsional untuk countdown
        end_time = None
        if END_DATETIME:
            try:
                dt = datetime.strptime(END_DATETIME, "%Y-%m-%d %H:%M:%S")
                end_time = int(dt.timestamp())
                print(f"📅 Menggunakan tanggal berakhir: {END_DATETIME}")
            except Exception as e:
                print(f"⚠️ Format PRESENCE_END_DATETIME salah ({e}).")

        update_args = {
            "details": DETAILS if DETAILS else None,
            "state": STATE if STATE else None,
            "large_image": LARGE_IMAGE if LARGE_IMAGE else None,
            "large_text": LARGE_TEXT if LARGE_TEXT else None,
            "small_image": SMALL_IMAGE if SMALL_IMAGE else None,
            "small_text": SMALL_TEXT if SMALL_TEXT else None,
            "start": start_time,
            "end": end_time,
        }

        if PARTY_SIZE and PARTY_MAX:
            try:
                update_args["party_size"] = [int(PARTY_SIZE), int(PARTY_MAX)]
                if PARTY_ID:
                    update_args["party_id"] = PARTY_ID
                if JOIN_SECRET:
                    update_args["join"] = JOIN_SECRET
                print(f"👥 Party/Squad: {PARTY_SIZE}/{PARTY_MAX}")
            except ValueError:
                print("⚠️ Gagal memproses party_size atau party_max. Harap isi dengan angka.")

        buttons = []
        if BUTTON_LABEL_1 and BUTTON_URL_1:
            buttons.append({"label": BUTTON_LABEL_1, "url": BUTTON_URL_1})
        if BUTTON_LABEL_2 and BUTTON_URL_2:
            buttons.append({"label": BUTTON_LABEL_2, "url": BUTTON_URL_2})
        if buttons:
            update_args["buttons"] = buttons
            print(f"🔗 Tombol ditambahkan: {[b['label'] for b in buttons]}")

        # Kirim update ke Discord Desktop
        rpc.update(**update_args)
        print("✨ Rich Presence berhasil aktif!")
        print(f"📝 Details: {DETAILS}")
        print(f"📝 State: {STATE}")
        print(f"🖼️ Large Image: {LARGE_IMAGE}")
        
        print("\nTekan Ctrl+C untuk berhenti...")

        while True:
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\n👋 Mematikan Rich Presence...")
        try:
            rpc.clear()
            rpc.close()
        except:
            pass
        print("✅ Selesai.")
    except Exception as e:
        print(f"❌ Terjadi kesalahan: {e}")
        print("Pastikan aplikasi Discord Desktop Anda sedang terbuka/berjalan di PC ini.")

if __name__ == "__main__":
    start_presence()
