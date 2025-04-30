from PyQt5.QtWidgets import QApplication
import sys
from src.services.camera_service import create_video_workers
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Buat video workers untuk semua kamera
    video_workers = create_video_workers()
    
    # Buat window utama dengan video workers yang sama
    main_window = MainWindow(video_workers)
    
    # Tampilkan window utama
    main_window.show()
    
    # Jalankan event loop
    app.exec_()
    
    # Bersihkan resources saat aplikasi ditutup
    for worker in video_workers:
        worker.stop()
        worker.wait()

if __name__ == '__main__':
    main()