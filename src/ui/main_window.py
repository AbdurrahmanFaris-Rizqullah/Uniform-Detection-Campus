#monitoring preview bideo kee 2 camera serta menampilkan deteksi seragam

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QDesktopWidget)
from PyQt5.QtCore import Qt, QPoint
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
            
            # Dapatkan ukuran layar dan hitung proporsi
            self.screen = QDesktopWidget().availableGeometry()
            self.screen_width = self.screen.width()
            self.screen_height = self.screen.height()
            
            # Hitung ukuran window dan posisi
            self.window_width = int(self.screen_width * 0.95) 
            self.window_height = int(self.screen_height * 0.95)
            center_x = (self.screen_width - self.window_width) // 2
            center_y = (self.screen_height - self.window_height) // 2
            
            # Set ukuran dan posisi window
            self.setGeometry(center_x, center_y, self.window_width, self.window_height)
            self.setStyleSheet(self.WINDOW_STYLE)
            self.showFullScreen()

            # Hitung ukuran preview dengan aspect ratio 16:9
            self.calculate_preview_sizes()

            # Inisialisasi counter (sama seperti sebelumnya)
            self.uniform_count = 0
            self.non_uniform_count = 0
            self.seragam_counts = {
                "azko": 0,
                "kawan_lama@ungu": 0,
                "kawan_lama@abu": 0,
                "informa": 0,
                "driver_informa": 0,
                "distribution_center": 0,
                "service_center": 0,
                "cipta_selera": 0,
                "elite": 0,
                "non_uniform": 0,
                "kawan_lama@driver": 0
            }

            # Setup layout dasar
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout()
            main_widget.setLayout(main_layout)

            # Setup layouts
            cameras_layout = self.setup_camera_preview()
            counter_layout = self.setup_counter_section()
            seragam_layout = self.setup_seragam_counter()

            # Gabungkan layouts dengan spacing proporsional
            main_layout.addLayout(cameras_layout, stretch=6)  # 60% tinggi
            main_layout.addLayout(counter_layout, stretch=2)  # 20% tinggi
            main_layout.addLayout(seragam_layout, stretch=2)  # 20% tinggi

            # Setup video workers
            self.setup_video_workers(video_workers)

    def calculate_preview_sizes(self):
        """Hitung ukuran preview yang optimal dengan aspect ratio 16:9"""
        target_ratio = 16/9
        
        # Hitung ukuran maksimum yang mungkin
        max_width = int(self.window_width * 0.52)  # Naikan dari 0.45 ke 0.65
        max_height = int(self.window_height * 0.8)  # Naikan dari 0.6 ke 0.7
        
        # Hitung ukuran berdasarkan aspect ratio
        if max_width/max_height > target_ratio:
            self.preview_width = int(max_height * target_ratio)
            self.preview_height = max_height
        else:
            self.preview_width = max_width
            self.preview_height = int(max_width / target_ratio)
        print(f"Preview size: {self.preview_width}x{self.preview_height}")

   
    def setup_camera_preview(self):
        cameras_layout = QHBoxLayout()
        cameras_layout.setSpacing(int(self.window_width * 0.01))
        self.camera_labels = []

        for i in range(2):
            camera_label = QLabel(f"PREVIEW CH{i+1}")
            camera_label.setStyleSheet(self.CAMERA_STYLE)
            camera_label.setAlignment(Qt.AlignCenter)
            
            # Gunakan ukuran yang sudah dihitung
            camera_label.setMinimumSize(self.preview_width, self.preview_height)
            camera_label.setMaximumSize(self.preview_width, self.preview_height)
            
            cameras_layout.addWidget(camera_label)
            self.camera_labels.append(camera_label)

        return cameras_layout

    def setup_counter_section(self):
        counter_layout = QHBoxLayout()
        counter_layout.setSpacing(int(self.window_width * 0.05))

        # Drawing button dengan ukuran proporsional
        self.open_drawing_btn = QPushButton("Buka Drawing Window")
        self.open_drawing_btn.setStyleSheet(self.BUTTON_STYLE)
        button_width = int(self.window_width * 0.15)
        self.open_drawing_btn.setMinimumWidth(button_width)
        self.open_drawing_btn.clicked.connect(self.open_drawing_window)
        counter_layout.addWidget(self.open_drawing_btn)
        counter_layout.addStretch(2)

        # Counters dengan ukuran proporsional
        uniform_width = int(self.window_width * 0.08)
        non_uniform_width = int(self.window_width * 0.11)
        counter_layout.addLayout(self.create_counter("UNIFORM", uniform_width))
        counter_layout.addLayout(self.create_counter("NON-UNIFORM", non_uniform_width))
        counter_layout.addStretch(3)

        return counter_layout

    def create_counter(self, label_text, width):
        counter = QVBoxLayout()
        counter.setSpacing(int(self.window_height * 0.01))

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
            self.uniform_count_label = count
        else:
            self.non_uniform_label = label
            self.non_uniform_count_label = count
        
        return counter

    def setup_seragam_counter(self):
        seragam_layout = QHBoxLayout()
        # Kurangi spacing agar tidak terlalu lebar
        seragam_layout.setSpacing(int(self.window_width * 0.01))  # 1% dari lebar

        jenis_seragam = [
            "Azko", "Informa", "Driver Informa", "kawan Lama ungu", "kawan Lama abu",
            "kawan Lama driver", "Distribution Center", "Service Center", 
            "Cipta selera", "elite", "non-uniform",
        ]

        # Hitung ukuran berdasarkan jumlah item
        total_items = len(jenis_seragam)
        available_width = self.window_width * 0.9  # 90% dari lebar window
        seragam_width = int(available_width / total_items)  # Bagi rata
        
        # Pastikan ukuran minimum dan maksimum
        seragam_width = max(120, min(seragam_width, 200))  # Minimal 120px, maksimal 200px
        seragam_height = int(self.window_height * 0.03)    # 3% dari tinggi

        self.nama_labels = []
        self.counter_values = {seragam: 0 for seragam in jenis_seragam}

        # Buat container untuk scroll jika terlalu panjang
        for seragam in jenis_seragam:
            container = QWidget()
            container_layout = QVBoxLayout(container)
            # Kurangi spacing
            container_layout.setSpacing(1)
            # Kurangi margin
            margin = 2  # Fixed margin kecil
            container_layout.setContentsMargins(margin, margin, margin, margin)

            nama_label = QLabel(seragam)
            nama_label.setAlignment(Qt.AlignCenter)
            nama_label.setStyleSheet(self.SERAGAM_LABEL_STYLE)
            nama_label.setFixedWidth(seragam_width)
            nama_label.setFixedHeight(seragam_height)
            nama_label.offset = 0
            nama_label.original_text = seragam
            self.nama_labels.append(nama_label)

            counter_label = QLabel("0")
            counter_label.setAlignment(Qt.AlignCenter)
            counter_label.setStyleSheet(self.SERAGAM_COUNTER_STYLE)
            counter_label.setFixedWidth(seragam_width)
            counter_label.setFixedHeight(seragam_height)

            container_layout.addWidget(nama_label)
            container_layout.addWidget(counter_label)

            self.seragam_counters[seragam] = counter_label
            seragam_layout.addWidget(container)

        # Tambahkan stretch di awal dan akhir untuk centering
        seragam_layout.addStretch(1)
        seragam_layout.insertStretch(0, 1)

        return seragam_layout

    def setup_video_workers(self, video_workers):
        self.video_workers = []
        config = load_config()
        for i in range(1, 3):
            camera_config = config['cameras'][f'camera_{i}']
            if os.path.exists(camera_config['source']):
                worker = VideoWorker(camera_config, i-1)
                worker.frame_ready.connect(self.update_video_feed)
                # Ubah koneksi signal counter langsung ke VideoWorker
                worker.update_counter.connect(self.update_counters)
                self.video_workers.append(worker)
                worker.start()
    
    def update_video_feed(self, frame, camera_id):
        """Update preview video dengan frame baru"""
        # Resize frame sesuai ukuran preview yang sudah dihitung
        frame_resized = cv2.resize(frame, (self.preview_width, self.preview_height), 
                                 interpolation=cv2.INTER_AREA)
        rgb_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * self.preview_width
        qt_image = QImage(rgb_frame.data, self.preview_width, self.preview_height, 
                         bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        if 0 <= camera_id < len(self.camera_labels):
            camera_label = self.camera_labels[camera_id]
            scaled_pixmap = pixmap.scaled(camera_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.draw_lines(scaled_pixmap, camera_id)
            camera_label.setPixmap(scaled_pixmap)

    def draw_lines(self, pixmap, camera_id):
        """Gambar garis border dan area prediksi di atas frame dengan scaling presisi ke QLabel preview"""
        try:
            config = load_config()
            if 'coordinates' not in config:
                return
            coordinates = config['coordinates']
            if str(camera_id) not in coordinates:
                return
            camera_coords = coordinates[str(camera_id)]
            label = self.camera_labels[camera_id]
            
            # Dapatkan ukuran sebenarnya dari pixmap yang sudah di-scale
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            
            # Basis koordinat dari drawing window
            base_width = 1280
            base_height = 720
            
            # Hitung faktor scaling berdasarkan ukuran pixmap yang sudah di-scale
            scale_x = pixmap_width / base_width
            scale_y = pixmap_height / base_height
            
            painter = QPainter(pixmap)
            # Border (hijau)
            if 'border' in camera_coords and camera_coords['border']:
                border_pen = QPen(QColor('#2ecc71'), 2, Qt.SolidLine)
                painter.setPen(border_pen)
                points = camera_coords['border']
                for i in range(len(points)):
                    x1 = int(points[i][0] * scale_x)
                    y1 = int(points[i][1] * scale_y)
                    x2 = int(points[(i+1)%len(points)][0] * scale_x)
                    y2 = int(points[(i+1)%len(points)][1] * scale_y)
                    painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
            # Area prediksi (biru)
            if 'area_pred' in camera_coords and camera_coords['area_pred']:
                area_pen = QPen(QColor('#3498db'), 2, Qt.SolidLine)
                painter.setPen(area_pen)
                points = camera_coords['area_pred']
                for i in range(len(points)):
                    x1 = int(points[i][0] * scale_x)
                    y1 = int(points[i][1] * scale_y)
                    x2 = int(points[(i+1)%len(points)][0] * scale_x)
                    y2 = int(points[(i+1)%len(points)][1] * scale_y)
                    painter.drawLine(QPoint(x1, y1), QPoint(x2, y2))
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
    
    def update_counters(self, class_name):
        try:
            # Update counter seragam
            if class_name in self.seragam_counts:
                self.seragam_counts[class_name] += 1
                display_name = seragam_mapping.get(class_name, class_name)
                if display_name in self.seragam_counters:
                    self.seragam_counters[display_name].setText(str(self.seragam_counts[class_name]))
                    print(f"Counter updated for {display_name}: {self.seragam_counts[class_name]}")
                
                # Update total counter
                if class_name == "non_uniform":
                    self.non_uniform_count += 1
                    if hasattr(self, 'non_uniform_count_label'):
                        self.non_uniform_count_label.setText(str(self.non_uniform_count))
                        print(f"Non-uniform total updated: {self.non_uniform_count}")
                else:  # Pindahkan ke luar if untuk menghitung semua seragam non-uniform
                    self.uniform_count += 1
                    if hasattr(self, 'uniform_count_label'):
                        self.uniform_count_label.setText(str(self.uniform_count))
                        print(f"Uniform total updated: {self.uniform_count}")
        except Exception as e:
            print(f"Error updating counters: {str(e)}")

    def open_drawing_window(self):
        """Buka window untuk menggambar area deteksi dengan singleton pattern"""
        from src.ui.drawing_window import DrawingWindow
        self.drawing_window = DrawingWindow.get_instance(video_workers=self.video_workers)
        self.drawing_window.show()  # ngemunculkan drawing window

seragam_mapping = {
    "azko": "Azko",
    "kawan_lama@ungu": "kawan Lama ungu",
    "kawan_lama@abu": "kawan Lama abu",
    "informa": "Informa",
    "driver_informa": "Driver Informa",
    "distribution_center": "Distribution Center",
    "service_center": "Service Center",
    "cipta_selera": "Cipta selera",
    "elite": "elite",
    "non_uniform": "non_uniform",
    "kawan_lama@driver": "Kawan Lama Driver"  
}
