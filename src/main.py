from PyQt5.QtWidgets import QApplication
import sys
from src.services.camera_service import start_camera_services
from src.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Mulai layanan kamera
    camera_services = start_camera_services()
    
    # Buat window utama
    main_window = MainWindow()
    
    # Hubungkan sinyal frame_ready dari setiap kamera ke main window
    for service in camera_services:
        service.frame_ready.connect(main_window.update_video_feed)
    
    # Tampilkan window utama
    main_window.show()
    
    # Jalankan event loop
    app.exec_()
    
    # Bersihkan resources saat aplikasi ditutup
    for service in camera_services:
        service.stop()
        service.wait()

if __name__ == '__main__':
    main()