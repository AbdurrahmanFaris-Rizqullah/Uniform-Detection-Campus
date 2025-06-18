import sqlite3
import os
import logging
import datetime

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Inisialisasi database dan buat tabel jika belum ada"""
        try:
            # Pastikan direktori database ada
            db_dir = os.path.dirname(self.db_path)
            os.makedirs(db_dir, exist_ok=True)
            logging.info(f"Direktori database dibuat/ditemukan di: {db_dir}")
            
            conn = sqlite3.connect(self.db_path)
            logging.info(f"Database berhasil dibuat/terhubung di: {self.db_path}")
            cursor = conn.cursor()
            
            # Buat tabel settings
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_code TEXT NOT NULL UNIQUE,
                    setting_name TEXT NOT NULL,
                    setting_value TEXT
                )
            """)
            # Buat tabel counting_log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS counting_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    camera_id INTEGER,
                    class TEXT,
                    count INTEGER
                )
            """)
            
            conn.commit()
            logging.info("Tabel settings & counting_log berhasil dibuat/diverifikasi")
        except Exception as e:
            logging.error(f"Gagal menginisialisasi database: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
    # ---- FUNGSI UNTUK COUNTING LOG ----
    def save_count(self, camera_id, class_name, count):
        """Simpan data counting ke tabel counting_log"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO counting_log (timestamp, camera_id, class, count) VALUES (?, ?, ?, ?)",
                (datetime.datetime.now().isoformat(), camera_id, class_name, count)
            )
            conn.commit()
            logging.info(f"Counting log disimpan: kamera={camera_id}, class={class_name}, count={count}")
        except Exception as e:
            logging.error(f"Gagal menyimpan counting log: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_all_counting_logs(self):
        """Ambil semua data counting log"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM counting_log")
            logs = cursor.fetchall()
            return logs
        except Exception as e:
            logging.error(f"Gagal mengambil counting logs: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    # --- FUNGSI SETTINGS TETAP SEPERTI AWAL ---
    def get_setting(self, setting_code):
        """Ambil nilai setting berdasarkan kode"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_code = ?",
                (setting_code,)
            )
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logging.error(f"Gagal mengambil setting: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def set_setting(self, setting_code, setting_name, setting_value):
        """Simpan atau update setting"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (setting_code, setting_name, setting_value)
                VALUES (?, ?, ?)
                ON CONFLICT(setting_code) DO UPDATE SET
                    setting_name = excluded.setting_name,
                    setting_value = excluded.setting_value
            """, (setting_code, setting_name, setting_value))
            conn.commit()
            logging.info(f"Setting {setting_code} berhasil disimpan/diupdate")
        except Exception as e:
            logging.error(f"Gagal menyimpan setting: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def delete_setting(self, setting_code):
        """Hapus setting berdasarkan kode"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM settings WHERE setting_code = ?",
                (setting_code,)
            )
            conn.commit()
            logging.info(f"Setting {setting_code} berhasil dihapus")
        except Exception as e:
            logging.error(f"Gagal menghapus setting: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def get_all_settings(self):
        """Ambil semua settings"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings")
            settings = cursor.fetchall()
            return settings
        except Exception as e:
            logging.error(f"Gagal mengambil semua settings: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

if __name__ == '__main__':
    # Tentukan path default untuk database
    default_db_path = os.path.join(os.path.dirname(__file__), 'settings.db')
    # Inisialisasi database
    db = Database(default_db_path)
    logging.info(f"Database berhasil dibuat di: {default_db_path}")

    # Contoh penggunaan fungsi counting baru
    db.save_count(camera_id=1, class_name='person', count=5)
    logs = db.get_all_counting_logs()
    print(logs)