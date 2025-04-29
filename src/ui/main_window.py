#monitoring preview bideo kee 2 camera serta menampilkan deteksi seragam

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import cv2
import os
from src.utils.config import load_config
from src.services.camera_service import VideoWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Inisialisasi dictionary untuk counter seragam
        self.seragam_counters = {}
        
        self.setWindowTitle("Sistem Deteksi Seragam")
        self.setGeometry(100, 100, 1920, 1200)
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #2c3e50, stop:1 #3498db);
            }
            QWidget {
                color: #ecf0f1;
            }
        """)
        
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
        camera_style = """
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                font-size: 36px;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """
        self.camera_label1.setStyleSheet(camera_style)
        self.camera_label1.setAlignment(Qt.AlignCenter)
        self.camera_label1.setMinimumSize(960, 720)
        cameras_layout.addWidget(self.camera_label1)
        
        # Preview kamera 2
        self.camera_label2 = QLabel("PREVIEW CH2")
        self.camera_label2.setStyleSheet(camera_style)
        self.camera_label2.setAlignment(Qt.AlignCenter)
        self.camera_label2.setMinimumSize(960, 720)
        cameras_layout.addWidget(self.camera_label2)

        # Layout counter dengan jarak yang lebih rapi
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(100)
        
        # Add drawing button
        self.open_drawing_btn = QPushButton("Buka Drawing Window")
        self.open_drawing_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #2980b9, stop:1 #2472a4);
            }
            QPushButton:pressed {
                background: #2472a4;
            }
        """)
        self.open_drawing_btn.clicked.connect(self.open_drawing_window)
        counter_layout.addWidget(self.open_drawing_btn)
        
        # Tambah stretch di awal dengan proporsi lebih kecil
        counter_layout.addStretch(2)
        
        # Counter UNIFORM
        counter_left = QVBoxLayout()
        counter_left.setSpacing(2)
        
        self.uniform_label = QLabel("UNIFORM")
        counter_label_style = """
            QLabel {
                color: #e74c3c;
                font-size: 24px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 8px;
                padding: 8px;
            }
        """
        counter_value_style = """
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #ecf0f1;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
            }
        """
        self.uniform_label.setStyleSheet(counter_label_style)
        self.uniform_label.setFixedWidth(150)
        self.uniform_label.setAlignment(Qt.AlignCenter)
        
        self.uniform_count = QLabel("0")
        self.uniform_count.setStyleSheet(counter_value_style)
        self.uniform_count.setAlignment(Qt.AlignCenter)
        
        counter_left.addWidget(self.uniform_label)
        counter_left.addWidget(self.uniform_count)
        
        # Counter NON-UNIFORM
        counter_right = QVBoxLayout()
        counter_right.setSpacing(2)
        
        self.non_uniform_label = QLabel("NON-UNIFORM")
        self.non_uniform_label.setStyleSheet(counter_label_style)
        self.non_uniform_label.setFixedWidth(220)
        self.non_uniform_label.setAlignment(Qt.AlignCenter)
        
        self.non_uniform_count = QLabel("0")
        self.non_uniform_count.setStyleSheet(counter_value_style)
        self.non_uniform_count.setAlignment(Qt.AlignCenter)
        
        counter_right.addWidget(self.non_uniform_label)
        counter_right.addWidget(self.non_uniform_count)
        
        # Tambahkan counter ke layout utama
        counter_layout.addLayout(counter_left)
        counter_layout.addLayout(counter_right)
        
        # Tambah stretch di akhir dengan proporsi lebih besar
        counter_layout.addStretch(2)
        
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
                    padding: 8px; 
                    color: #ecf0f1;
                    font-weight: bold;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                             stop:0 #2c3e50, stop:1 #34495e);
                    border-radius: 5px;
                    border: 1px solid #2980b9;
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
                    padding: 8px; 
                    color: #2ecc71;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 5px;
                    border: 1px solid #27ae60;
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
        config = load_config()
        for i in range(1, 3):  # For camera 1 and 2
            camera_config = config['cameras'][f'camera_{i}']
            # Hanya buat worker jika source video tersedia
            if os.path.exists(camera_config['source']):
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
        
        # Buat pixmap yang dapat digambar
        if camera_id == 0:
            scaled_pixmap = pixmap.scaled(self.camera_label1.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            # Gambar garis di atas frame
            self.draw_lines(scaled_pixmap, camera_id)
            self.camera_label1.setPixmap(scaled_pixmap)
        else:
            scaled_pixmap = pixmap.scaled(self.camera_label2.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            # Gambar garis di atas frame
            self.draw_lines(scaled_pixmap, camera_id)
            self.camera_label2.setPixmap(scaled_pixmap)

    def draw_lines(self, pixmap, camera_id):
        """Gambar garis border dan area prediksi di atas frame"""
        try:
            # Load koordinat dari config
            config = load_config()
            if 'coordinates' not in config:
                return
            
            coordinates = config['coordinates']
            if str(camera_id) not in coordinates:
                return
            
            camera_coords = coordinates[str(camera_id)]
            
            # Buat painter untuk menggambar
            painter = QPainter(pixmap)
            
            # Set pen untuk border (hijau)
            if 'border' in camera_coords and camera_coords['border']:
                border_pen = QPen(QColor('#2ecc71'), 2, Qt.SolidLine)
                painter.setPen(border_pen)
                points = camera_coords['border']
                for i in range(len(points)):
                    start = QPoint(points[i][0], points[i][1])
                    end = QPoint(points[(i+1)%len(points)][0], points[(i+1)%len(points)][1])
                    painter.drawLine(start, end)
            
            # Set pen untuk area prediksi (biru)
            if 'area_pred' in camera_coords and camera_coords['area_pred']:
                area_pen = QPen(QColor('#3498db'), 2, Qt.SolidLine)
                painter.setPen(area_pen)
                points = camera_coords['area_pred']
                for i in range(len(points)):
                    start = QPoint(points[i][0], points[i][1])
                    end = QPoint(points[(i+1)%len(points)][0], points[(i+1)%len(points)][1])
                    painter.drawLine(start, end)
            
            painter.end()
        except Exception as e:
            print(f"Error drawing lines: {str(e)}")
            return

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
            
    def open_drawing_window(self):
        """Buka window untuk menggambar area deteksi"""
        from src.ui.drawing_window import DrawingWindow
        self.drawing_window = DrawingWindow()
        self.drawing_window.show()
