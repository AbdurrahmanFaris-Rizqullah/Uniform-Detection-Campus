import sys # Import modul sistem yang dibutuhkan
sys.path.append('src') # Tambahkan direktori src ke Python path untuk mengizinkan import dari folder src
from PyQt5.QtWidgets import QApplication # Import class QApplication dari PyQt5 untuk membuat instance aplikasi
from ui.main_window import MainWindow # Import class MainWindow kustom dari modul ui

def main():
    app = QApplication(sys.argv) # Buat instance QApplication dengan argumen command line
    window = MainWindow() # Buat instance window utama
    window.show() # Tampilkan window utama
    sys.exit(app.exec_()) # Mulai event loop aplikasi dan keluar dengan kode return-nya

if __name__ == '__main__': # Hanya jalankan fungsi main jika script ini dijalankan secara langsung (tidak diimport)
    main()