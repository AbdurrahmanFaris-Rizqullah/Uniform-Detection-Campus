from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QListWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
import cv2
import numpy as np
import json
import os
from src.utils.config import load_config
from src.ui.main_window import VideoWorker  # Import VideoWorker dari main_window

class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Detection Area")
        self.setGeometry(200, 200, 1280, 720)
        
        # Tambahkan atribut untuk video
        self.current_camera = 0  # Default ke kamera 1 (index 0)
        self.video_workers = []
        self.last_frames = [None, None]  # Simpan frame terakhir untuk setiap kamera
        
        # Atribut untuk drawing
        self.drawing = False
        self.drawing_mode = None  # 'border' atau 'area_pred'
        self.points = {0: {'border': [], 'area_pred': []}, 
                      1: {'border': [], 'area_pred': []}}  # Simpan koordinat untuk setiap kamera
        self.current_points = []  # Titik-titik yang sedang digambar
        
        # Load koordinat yang tersimpan
        self.load_coordinates()
        
        # Widget dan layout utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Layout utama (vertical) untuk toolbar dan preview
        main_container = QVBoxLayout()
        
        # Toolbar dengan tombol-tombol
        toolbar_layout = QHBoxLayout()
        
        # Tombol-tombol kontrol
        self.border_btn = QPushButton("Border")
        self.area_pred_btn = QPushButton("Area Pred")
        self.delete_btn = QPushButton("Delete")
        self.save_btn = QPushButton("Save")
        
        # Style untuk tombol
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """
        for btn in [self.border_btn, self.area_pred_btn, self.delete_btn, self.save_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)
        
        toolbar_layout.addStretch()
        
        # Layout untuk preview dan list
        content_layout = QHBoxLayout()
        
        # List kamera di sebelah kiri preview
        self.camera_list = QListWidget()
        self.camera_list.addItems(["Cam CH1", "Cam CH2"])
        self.camera_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                max-width: 150px;
                min-height: 600px;
                border: 1px solid #ddd;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
        """)
        
        # Preview/Drawing area yang digabung
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: white;
                min-height: 600px;
                min-width: 900px;
                font-size: 24px;
                border: 1px solid #ddd;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        # Susun layout
        content_layout.addWidget(self.camera_list)
        content_layout.addWidget(self.preview_label, stretch=1)
        
        main_container.addLayout(toolbar_layout)
        main_container.addLayout(content_layout)
        main_layout.addLayout(main_container)
        
        # Setup tools
        self.setup_tools()
        
        # Mulai video workers dengan lebih efisien
        config = load_config()
        for i in range(1, 3):  # Untuk kamera 1 dan 2
            camera_config = config['cameras'][f'camera_{i}']
            worker = VideoWorker(camera_config, i-1)  # i-1 untuk index 0-based
            worker.frame_ready.connect(self.store_frame)
            self.video_workers.append(worker)
            worker.start()
        
        # Pilih kamera pertama secara default
        self.camera_list.setCurrentRow(0)
        
        # Timer untuk update UI dengan interval yang lebih lama
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(50)  # 50ms = 20fps, cukup untuk preview yang smooth
        
    def setup_tools(self):
        """Setup event handlers dan tools"""
        self.border_btn.clicked.connect(self.activate_border_tool)
        self.area_pred_btn.clicked.connect(self.activate_area_pred_tool)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.save_btn.clicked.connect(self.save_drawing)
        self.camera_list.currentRowChanged.connect(self.show_camera_preview)  # Perbaikan di sini
    
    def activate_border_tool(self):
        """Aktifkan tool untuk menggambar border"""
        self.reset_button_styles()
        self.border_btn.setStyleSheet(self.border_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        self.drawing_mode = 'border'
        self.current_points = []
    
    def activate_area_pred_tool(self):
        """Aktifkan tool untuk menggambar area prediksi"""
        self.reset_button_styles()
        self.area_pred_btn.setStyleSheet(self.area_pred_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        self.drawing_mode = 'area_pred'
        self.current_points = []
    
    def reset_button_styles(self):
        """Reset style semua tombol"""
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 8px 15px;
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """
        for btn in [self.border_btn, self.area_pred_btn, self.delete_btn, self.save_btn]:
            btn.setStyleSheet(button_style)
    
    def delete_selected(self):
        """Hapus item yang dipilih"""
        if self.drawing_mode:
            self.points[self.current_camera][self.drawing_mode] = []
            self.current_points = []
            self.update_ui()
    
    def save_drawing(self):
        """Simpan hasil gambar ke file JSON"""
        config = load_config()
        save_dir = os.path.join(os.path.dirname(config['config_path']), 'coordinates')
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, 'drawing_coordinates.json')
        with open(save_path, 'w') as f:
            json.dump(self.points, f)
        print(f"Koordinat tersimpan di: {save_path}")
    
    def load_coordinates(self):
        """Muat koordinat dari file JSON"""
        config = load_config()
        save_dir = os.path.join(os.path.dirname(config['config_path']), 'coordinates')
        save_path = os.path.join(save_dir, 'drawing_coordinates.json')
        
        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                try:
                    loaded_points = json.load(f)
                    # Konversi string key ke integer
                    self.points = {int(k): v for k, v in loaded_points.items()}
                    print(f"Koordinat dimuat dari: {save_path}")
                except json.JSONDecodeError:
                    print("Error saat memuat file koordinat")
    
    def show_camera_preview(self, index):
        """Tampilkan preview kamera yang dipilih"""
        print(f"Switching to camera {index}")  # Debug
        print(f"Current frames status: CH1: {'Available' if self.last_frames[0] is not None else 'None'}, "
              f"CH2: {'Available' if self.last_frames[1] is not None else 'None'}")  # Debug
        self.current_camera = index
        self.update_ui()

    def update_ui(self):
        """Update UI dengan frame terbaru"""
        print(f"Updating UI for camera {self.current_camera}")  # Debug
        
        if self.last_frames[self.current_camera] is not None:
            frame = self.last_frames[self.current_camera]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            # Tampilkan pesan "No Signal" untuk kamera yang tidak ada videonya
            self.preview_label.clear()
            self.preview_label.setText(f"NO SIGNAL\nCamera CH{self.current_camera + 1}")
    
    def store_frame(self, frame, camera_id):
        """Simpan frame untuk diproses nanti dengan optimasi memori"""
        # Hanya print jika frame berubah signifikan
        if self.last_frames[camera_id] is None:
            print(f"First frame received from camera {camera_id}")
        
        # Resize frame untuk preview jika terlalu besar
        if frame.shape[1] > 1280:  # Jika lebar > 1280
            scale = 1280.0 / frame.shape[1]
            frame = cv2.resize(frame, None, fx=scale, fy=scale,
                             interpolation=cv2.INTER_AREA)
        self.last_frames[camera_id] = frame

    def show_camera_preview(self, index):
        """Tampilkan preview kamera yang dipilih"""
        if self.current_camera != index:  # Hanya print saat benar-benar ganti kamera
            print(f"\nSwitching to camera {index}")
            print(f"Current frames status: CH1: {'Available' if self.last_frames[0] is not None else 'None'}, "
                  f"CH2: {'Available' if self.last_frames[1] is not None else 'None'}\n")
        self.current_camera = index
        self.update_ui()

    def update_ui(self):
        """Update UI dengan frame terbaru dan gambar"""
        if self.last_frames[self.current_camera] is not None:
            frame = self.last_frames[self.current_camera].copy()
            
            # Gambar titik-titik yang tersimpan
            if self.points[self.current_camera]['border']:
                cv2.polylines(frame, [np.array(self.points[self.current_camera]['border'])], 
                             True, (0, 255, 0), 2)
            if self.points[self.current_camera]['area_pred']:
                cv2.polylines(frame, [np.array(self.points[self.current_camera]['area_pred'])], 
                             True, (255, 0, 0), 2)
            
            # Gambar titik-titik yang sedang digambar
            if self.current_points:
                color = (0, 255, 0) if self.drawing_mode == 'border' else (255, 0, 0)
                for point in self.current_points:
                    cv2.circle(frame, tuple(point), 3, color, -1)
                if len(self.current_points) > 1:
                    cv2.polylines(frame, [np.array(self.current_points)], False, color, 2)
            
            # Konversi frame ke QPixmap
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.clear()
            self.preview_label.setText(f"NO SIGNAL\nCamera CH{self.current_camera + 1}")
    
    def closeEvent(self, event):
        """Bersihkan video workers dan simpan koordinat saat window ditutup"""
        self.update_timer.stop()
        for worker in self.video_workers:
            worker.stop()
        self.save_drawing()
        super().closeEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click untuk menambah titik"""
        if not self.drawing_mode or not self.last_frames[self.current_camera] is not None:
            return
        
        # Konversi koordinat mouse ke koordinat frame
        pos = self.preview_label.mapFrom(self, event.pos())
        if not self.preview_label.rect().contains(pos):
            return
            
        # Hitung skala dan offset
        frame = self.last_frames[self.current_camera]
        label_size = self.preview_label.size()
        frame_h, frame_w = frame.shape[:2]
        scale = min(label_size.width() / frame_w, label_size.height() / frame_h)
        
        # Hitung offset untuk centering
        x_offset = (label_size.width() - frame_w * scale) / 2
        y_offset = (label_size.height() - frame_h * scale) / 2
        
        # Konversi koordinat
        x = int((pos.x() - x_offset) / scale)
        y = int((pos.y() - y_offset) / scale)
        
        # Tambahkan titik jika valid
        if 0 <= x < frame_w and 0 <= y < frame_h:
            self.current_points.append([x, y])
            self.update_ui()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click untuk mengakhiri gambar"""
        if not self.drawing_mode or not self.current_points:
            return
            
        # Simpan titik-titik ke points
        self.points[self.current_camera][self.drawing_mode] = self.current_points.copy()
        self.current_points = []
        self.update_ui()