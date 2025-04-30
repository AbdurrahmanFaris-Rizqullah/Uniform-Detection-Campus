#monitoring preview bideo kee 2 camera serta menampilkan deteksi seragam

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import cv2
import os
from src.utils.config import load_config
from src.services.camera_service import VideoWorker

class MainWindow(QMainWindow):
#----------------------STYLE SHEET----------------------#
    WINDOW_STYLE = """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                      stop:0 #2c3e50, stop:1 #3498db);
        }
        QWidget {
            color: #ecf0f1;
        }
    """

    CAMERA_STYLE = """
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

    BUTTON_STYLE = """
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
    """

    COUNTER_LABEL_STYLE = """
        QLabel {
            color: #e74c3c;
            font-size: 24px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 8px;
        }
    """

    COUNTER_VALUE_STYLE = """
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

    SERAGAM_LABEL_STYLE = """
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
    """

    SERAGAM_COUNTER_STYLE = """
        QLabel { 
            font-size: 20px; 
            padding: 8px; 
            color: #2ecc71;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 5px;
            border: 1px solid #27ae60;
        }
    """
#----------------------STYLE SHEET----------------------#


    def __init__(self, video_workers=None):
        super().__init__()
        self.seragam_counters = {}
        self.setWindowTitle("Sistem Deteksi Seragam")
        self.setGeometry(100, 100, 1920, 1200)
        self.setStyleSheet(self.WINDOW_STYLE)

        # Setup layout dasar
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Setup camera preview
        cameras_layout = self.setup_camera_preview()

        # Setup counter section
        counter_layout = self.setup_counter_section()

        # Setup seragam counter
        seragam_layout = self.setup_seragam_counter()

        # Gabungkan semua layout
        main_layout.addLayout(cameras_layout)
        main_layout.addLayout(counter_layout)
        main_layout.addLayout(seragam_layout)

        # Setup video workers
        self.setup_video_workers(video_workers)

    def setup_camera_preview(self):
        cameras_layout = QHBoxLayout()
        cameras_layout.setSpacing(5)
        self.camera_labels = []

        for i in range(2):
            camera_label = QLabel(f"PREVIEW CH{i+1}")
            camera_label.setStyleSheet(self.CAMERA_STYLE)
            camera_label.setAlignment(Qt.AlignCenter)
            camera_label.setMinimumSize(960, 720)
            cameras_layout.addWidget(camera_label)
            self.camera_labels.append(camera_label)

        return cameras_layout

    def setup_counter_section(self):
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(100)

        # Drawing button
        self.open_drawing_btn = QPushButton("Buka Drawing Window")
        self.open_drawing_btn.setStyleSheet(self.BUTTON_STYLE)
        self.open_drawing_btn.clicked.connect(self.open_drawing_window)
        counter_layout.addWidget(self.open_drawing_btn)
        counter_layout.addStretch(2)

        # Uniform counter
        counter_layout.addLayout(self.create_counter("UNIFORM", 150))
        counter_layout.addLayout(self.create_counter("NON-UNIFORM", 220))
        counter_layout.addStretch(2)

        return counter_layout

    def create_counter(self, label_text, width):
        counter = QVBoxLayout()
        counter.setSpacing(2)

        label = QLabel(label_text)
        label.setStyleSheet(self.COUNTER_LABEL_STYLE)
        label.setFixedWidth(width)
        label.setAlignment(Qt.AlignCenter)

        count = QLabel("0")
        count.setStyleSheet(self.COUNTER_VALUE_STYLE)
        count.setAlignment(Qt.AlignCenter)

        counter.addWidget(label)
        counter.addWidget(count)

        if label_text == "UNIFORM":
            self.uniform_label = label
            self.uniform_count = count
        else:
            self.non_uniform_label = label
            self.non_uniform_count = count

        return counter

    def setup_seragam_counter(self):
        seragam_layout = QHBoxLayout()
        seragam_layout.setSpacing(50)

        jenis_seragam = [
            "Azko", "Informa", "Driver Informa", "kawan Lama ungu", "kawan Lama abu",
            "Distribution Center", "Service Center", "Cipta selera", "elite"
        ]

        self.nama_labels = []
        self.counter_values = {seragam: 0 for seragam in jenis_seragam}

        for seragam in jenis_seragam:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setSpacing(2)
            container_layout.setContentsMargins(5, 5, 5, 5)

            nama_label = QLabel(seragam)
            nama_label.setAlignment(Qt.AlignCenter)
            nama_label.setStyleSheet(self.SERAGAM_LABEL_STYLE)
            nama_label.setFixedWidth(160)
            nama_label.setFixedHeight(30)
            nama_label.offset = 0
            nama_label.original_text = seragam + " " * 20
            self.nama_labels.append(nama_label)

            counter_label = QLabel("0")
            counter_label.setAlignment(Qt.AlignCenter)
            counter_label.setStyleSheet(self.SERAGAM_COUNTER_STYLE)
            counter_label.setFixedWidth(160)
            counter_label.setFixedHeight(30)

            container_layout.addWidget(nama_label)
            container_layout.addWidget(counter_label)

            self.seragam_counters[seragam] = counter_label
            seragam_layout.addWidget(container)

        return seragam_layout

    def setup_video_workers(self, video_workers):
        self.video_workers = []
        config = load_config()
        for i in range(1, 3):
            camera_config = config['cameras'][f'camera_{i}']
            if os.path.exists(camera_config['source']):
                worker = VideoWorker(camera_config, i-1)
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
        if 0 <= camera_id < len(self.camera_labels):
            camera_label = self.camera_labels[camera_id]
            scaled_pixmap = pixmap.scaled(camera_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            # Gambar garis di atas frame
            self.draw_lines(scaled_pixmap, camera_id)
            camera_label.setPixmap(scaled_pixmap)

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
        """Buka window untuk menggambar area deteksi dengan singleton pattern"""
        from src.ui.drawing_window import DrawingWindow
        self.drawing_window = DrawingWindow.get_instance(video_workers=self.video_workers)
        # Hapus pemanggilan show() karena sudah ditangani di get_instance()
        # self.drawing_window.show()  # Fokus ke window yang sudah ada+
