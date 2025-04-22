from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
from src.utils.config import load_config  # Fix the import path

class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)
    
    def __init__(self, camera_config, camera_id):
        super().__init__()
        self.source = camera_config['source']
        self.resolution = camera_config['resolution']
        self.fps = camera_config['fps']
        self.camera_id = camera_id
        self.running = True
        self.frame_interval = 1.0 / (self.fps if self.fps > 0 else 30.0)  # Interval waktu antar frame
        self.last_frame_time = 0
        
    def run(self):
        import time
        cap = cv2.VideoCapture(self.source)
        if self.fps > 0:
            cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        while self.running:
            current_time = time.time()
            # Hanya proses frame jika sudah waktunya
            if current_time - self.last_frame_time >= self.frame_interval:
                ret, frame = cap.read()
                if ret:
                    # Resize frame untuk mengurangi beban memori
                    if frame.shape[1] > 1280:  # Jika lebar > 1280
                        scale = 1280.0 / frame.shape[1]
                        frame = cv2.resize(frame, None, fx=scale, fy=scale,
                                         interpolation=cv2.INTER_AREA)
                    self.frame_ready.emit(frame, self.camera_id)
                    self.last_frame_time = current_time
                else:
                    # Ulang video jika sudah selesai
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    time.sleep(0.1)  # Tambah delay kecil saat reset
            else:
                # Tidur sejenak untuk mengurangi penggunaan CPU
                time.sleep(0.001)
        cap.release()
        
    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inisialisasi dictionary untuk counter seragam
        self.seragam_counters = {}
        
        self.setWindowTitle("Sistem Deteksi Seragam")
        self.setGeometry(100, 100, 1920, 1200)
        
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama (vertical)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Layout preview cameras (horizontal)
        cameras_layout = QHBoxLayout()
        cameras_layout.setSpacing(5)  # Kurangi spacing antar kamera
        
        # Preview kamera 1
        self.camera_label1 = QLabel("PREVIEW CH1")
        self.camera_label1.setStyleSheet("QLabel { background-color: black; color: white; font-size: 36px; }")
        self.camera_label1.setAlignment(Qt.AlignCenter)
        self.camera_label1.setMinimumSize(960, 720)  # Ukuran lebih besar
        cameras_layout.addWidget(self.camera_label1)
        
        # Preview kamera 2
        self.camera_label2 = QLabel("PREVIEW CH2")
        self.camera_label2.setStyleSheet("QLabel { background-color: black; color: white; font-size: 36px; }")
        self.camera_label2.setAlignment(Qt.AlignCenter)
        self.camera_label2.setMinimumSize(960, 720)  # Ukuran lebih besar
        cameras_layout.addWidget(self.camera_label2)

        # Layout counter dengan jarak yang lebih rapi
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(800)
        
        # Add drawing button
        self.open_drawing_btn = QPushButton("Buka Drawing Window")
        self.open_drawing_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 5px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
            }
        """)
        counter_layout.addWidget(self.open_drawing_btn)
        
        # Tambah stretch di awal untuk mendorong ke tengah
        counter_layout.addStretch()
        
        # Counter UNIFORM
        counter_left = QVBoxLayout()
        counter_left.setSpacing(2)
        
        self.uniform_label = QLabel("UNIFORM")
        self.uniform_label.setStyleSheet("QLabel { color: red; font-size: 24px; font-weight: bold; }")
        self.uniform_label.setFixedWidth(150)
        self.uniform_label.setAlignment(Qt.AlignCenter)
        
        self.uniform_count = QLabel("0")
        self.uniform_count.setStyleSheet("QLabel { font-size: 32px; font-weight: bold; }")
        self.uniform_count.setAlignment(Qt.AlignCenter)
        
        counter_left.addWidget(self.uniform_label)
        counter_left.addWidget(self.uniform_count)
        
        # Counter NON-UNIFORM
        counter_right = QVBoxLayout()
        counter_right.setSpacing(2)
        
        self.non_uniform_label = QLabel("NON-UNIFORM")
        self.non_uniform_label.setStyleSheet("QLabel { color: red; font-size: 24px; font-weight: bold; }")
        self.non_uniform_label.setFixedWidth(220)
        self.non_uniform_label.setAlignment(Qt.AlignCenter)
        
        self.non_uniform_count = QLabel("0")
        self.non_uniform_count.setStyleSheet("QLabel { font-size: 32px; font-weight: bold; }")
        self.non_uniform_count.setAlignment(Qt.AlignCenter)
        
        counter_right.addWidget(self.non_uniform_label)
        counter_right.addWidget(self.non_uniform_count)
        
        # Tambahkan counter ke layout utama
        counter_layout.addLayout(counter_left)
        counter_layout.addLayout(counter_right)
        
        # Tambah stretch di akhir untuk menyeimbangkan
        counter_layout.addStretch()
        
        # Layout Seragam counter dengan spacing yang lebih rapi
        seragam_layout = QHBoxLayout()  # Ubah ke HBoxLayout untuk satu baris
        seragam_layout.setSpacing(50)   # Jarak antar item
        
        # List seragam dari hasil anotasi
        jenis_seragam = [
            "Azko", "Informa", "Driver Informa", "kawan Lama ungu", "kawan Lama abu",
            "Distribution Center", "Service Center", "Cipta selera", "elite"
        ]
        
        # Inisialisasi list untuk label marquee
        self.nama_labels = []
        self.counter_values = {seragam: 0 for seragam in jenis_seragam}
        
        # Buat satu timer untuk semua marquee
        # self.marquee_timer = QTimer(self)
        # self.marquee_timer.timeout.connect(self.update_all_text)
        # self.marquee_timer.start(100)
        
        # Tambahkan seragam dalam satu baris
        for seragam in jenis_seragam:
            # Buat container widget untuk setiap seragam
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(2)
            container_layout.setContentsMargins(5, 5, 5, 5)
            
            # Label untuk nama seragam dengan marquee
            nama_label = QLabel(seragam)
            nama_label.setAlignment(Qt.AlignCenter)
            nama_label.setStyleSheet("""
                QLabel { 
                    font-size: 14px; 
                    padding: 2px; 
                    color: black;
                    font-weight: bold;
                    background-color: #f0f0f0;
                    border: 1px solid #ddd;
                }
            """)
            nama_label.setFixedWidth(160)
            nama_label.setFixedHeight(30)
            
            # Setup marquee untuk nama
            nama_label.offset = 0
            nama_label.original_text = seragam + " " * 20
            self.nama_labels.append(nama_label)
            
            # Label untuk counter
            counter_label = QLabel("0")
            counter_label.setAlignment(Qt.AlignCenter)
            counter_label.setStyleSheet("""
                QLabel { 
                    font-size: 20px; 
                    padding: 2px; 
                    color: black;
                    font-weight: bold;
                    background-color: white;
                    border: 1px solid #ddd;
                }
            """)
            counter_label.setFixedWidth(160)
            counter_label.setFixedHeight(30)
            
            container_layout.addWidget(nama_label)
            container_layout.addWidget(counter_label)
            
            self.seragam_counters[seragam] = counter_label
            seragam_layout.addWidget(container)

        # Menambahkan semua layout ke main layout
        main_layout.addLayout(cameras_layout)
        main_layout.addLayout(counter_layout)
        main_layout.addLayout(seragam_layout)

        # Setup video workers
        self.video_workers = []
        
        # Mulai video streams
        config = load_config()  # Add this import at top
        for i in range(1, 3):  # For camera 1 and 2
            camera_config = config['cameras'][f'camera_{i}']
            worker = VideoWorker(camera_config, i-1)  # i-1 for 0-based index
            worker.frame_ready.connect(self.update_video_feed)
            self.video_workers.append(worker)
            worker.start()

    def update_video_feed(self, frame, camera_id):
        """Update preview video dengan frame baru"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        if camera_id == 0:
            scaled_pixmap = pixmap.scaled(self.camera_label1.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.camera_label1.setPixmap(scaled_pixmap)
        else:
            scaled_pixmap = pixmap.scaled(self.camera_label2.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.camera_label2.setPixmap(scaled_pixmap)

    def closeEvent(self, event):
        """Bersihkan video workers saat window ditutup"""
        for worker in self.video_workers:
            worker.stop()
        super().closeEvent(event)

    def update_all_text(self):
        """Update semua teks counter dengan animasi"""
        for label in self.nama_labels:
            text = label.original_text
            label.offset = (label.offset + 1) % len(text)
            display_text = text[label.offset:] + text[:label.offset]
            label.setText(display_text)
    
    def update_counter(self, seragam_name, value):
        """Update nilai counter untuk seragam tertentu"""
        if seragam_name in self.counter_values:
            self.counter_values[seragam_name] = value
