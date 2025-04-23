import sqlite3
import os
import logging

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
            
            conn.commit()
            logging.info("Tabel settings berhasil dibuat/diverifikasi")
        except Exception as e:
            logging.error(f"Gagal menginisialisasi database: {str(e)}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
    
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