from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import yaml
from src.utils.config import load_config
from src.services.camera_service import VideoWorker  # Import VideoWorker dari camera_service

class DrawingWindow(QMainWindow):
    _instance = None
    _video_workers = None
    
    @classmethod
    def get_instance(cls, video_workers=None):
        if cls._instance is None:
            cls._instance = DrawingWindow(video_workers)
        else:
            cls._instance.activateWindow()
        
        if video_workers is not None and video_workers != cls._video_workers:
            cls._video_workers = video_workers
            cls._instance.update_video_workers(video_workers)
        
        return cls._instance
    
    def __init__(self, video_workers=None):
        print(f"[DEBUG] __init__ dipanggil. Instance saat ini: {DrawingWindow._instance}")
        if DrawingWindow._instance is not None:
            print("[DEBUG] Instance sudah ada, keluar dari __init__")
            return
        
        print("[DEBUG] Melanjutkan inisialisasi instance baru")
        super().__init__()
        # Simpan video workers di level kelas
        if video_workers is not None:
            DrawingWindow._video_workers = video_workers
        self.setWindowTitle("Drawing Detection Area")
        self.setGeometry(200, 200, 1280, 720)
        
        # Set window style untuk konsistensi dengan MainWindow
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #2c3e50, stop:1 #3498db);
            }
            QWidget {
                color: #ecf0f1;
            }
        """)
        
        # Tambahkan atribut untuk video
        self.current_camera = 0  # Default ke kamera 1 (index 0)
        self.video_workers = []
        self.last_frames = [None, None]  # Simpan frame terakhir untuk setiap kamera
        
        # Inisialisasi video workers
        self.update_video_workers(DrawingWindow._video_workers if DrawingWindow._video_workers else [])
        
    def update_video_workers(self, new_workers):
        """Update video workers dan koneksi sinyal"""
        # Hapus koneksi lama
        for worker in self.video_workers:
            try:
                worker.frame_ready.disconnect(self.store_frame)
            except TypeError:
                pass  # Abaikan jika tidak ada koneksi
        
        # Update workers dan buat koneksi baru
        self.video_workers = new_workers
        for worker in self.video_workers:
            worker.frame_ready.connect(self.store_frame)
        
        # Atribut untuk drawing
        self.drawing = False
        self.drawing_mode = None  # 'border' atau 'area_pred'
        self.is_drawing_enabled = False  # Status mode drawing
        self.points = {0: {'border': [], 'area_pred': []}, 
                      1: {'border': [], 'area_pred': []}}  # Simpan koordinat untuk setiap kamera
        self.current_points = []  # Titik-titik yang sedang digambar
        
        # Atribut untuk undo/redo
        self.undo_stack = []  # Stack untuk menyimpan state sebelumnya
        self.redo_stack = []  # Stack untuk menyimpan state yang di-undo
        self.max_undo = 20  # Batasi jumlah undo untuk menghemat memori
        
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
        self.toggle_drawing_btn = QPushButton("Mode Drawing: OFF")
        self.border_btn = QPushButton("Border")
        self.area_pred_btn = QPushButton("Area Pred")
        self.delete_btn = QPushButton("Delete")
        self.save_btn = QPushButton("Save")
        self.undo_btn = QPushButton("Undo")
        self.redo_btn = QPushButton("Redo")
        
        # Nonaktifkan tombol drawing tools di awal
        self.border_btn.setEnabled(False)
        self.area_pred_btn.setEnabled(False)
        
        # Nonaktifkan tombol undo/redo di awal
        self.undo_btn.setEnabled(False)
        self.redo_btn.setEnabled(False)
        
        # Style untuk tombol yang konsisten dengan MainWindow
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #2980b9, stop:1 #2472a4);
            }
            QPushButton:pressed {
                background: #2472a4;
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #95a5a6, stop:1 #7f8c8d);
                color: #bdc3c7;
            }
        """
        
        # Style khusus untuk tombol toggle yang konsisten dengan MainWindow
        toggle_style = """
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                margin: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #c0392b, stop:1 #962d22);
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #2ecc71, stop:1 #27ae60);
            }
            QPushButton:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #27ae60, stop:1 #219a52);
            }
        """
        
        self.toggle_drawing_btn.setStyleSheet(toggle_style)
        self.toggle_drawing_btn.setCheckable(True)
        toolbar_layout.addWidget(self.toggle_drawing_btn)
        
        for btn in [self.border_btn, self.area_pred_btn, self.delete_btn, self.save_btn, self.undo_btn, self.redo_btn]:
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
                background: rgba(0, 0, 0, 0.2);
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                color: #ecf0f1;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #3498db, stop:1 #2980b9);
            }
        """)
        
        # Status label untuk mode drawing
        self.status_label = QLabel("Mode: Normal")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 5px;
                color: white;
                background-color: #333;
                border-radius: 3px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedHeight(30)
        
        # Preview/Drawing area yang digabung
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                min-height: 720px;
                min-width: 1280px;
                font-size: 24px;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        # Susun layout
        content_layout.addWidget(self.camera_list)
        
        # Layout untuk preview dan status
        preview_container = QVBoxLayout()
        preview_container.addWidget(self.status_label)
        preview_container.addWidget(self.preview_label, stretch=1)
        content_layout.addLayout(preview_container, stretch=1)
        
        main_container.addLayout(toolbar_layout)
        main_container.addLayout(content_layout)
        main_layout.addLayout(main_container)
        
        # Setup tools
        self.setup_tools()
        
        # Hubungkan video workers yang ada ke store_frame
        for worker in self.video_workers:
            worker.frame_ready.connect(self.store_frame)
        
        # Pilih kamera pertama secara default
        self.camera_list.setCurrentRow(0)
        
        # Timer untuk update UI dengan interval yang lebih lama
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # 100ms = 10fps, cukup untuk preview interaktif
        
    def setup_tools(self):
        """Setup event handlers dan tools"""
        self.toggle_drawing_btn.clicked.connect(self.toggle_drawing_mode)
        self.border_btn.clicked.connect(self.activate_border_tool)
        self.area_pred_btn.clicked.connect(self.activate_area_pred_tool)
        self.delete_btn.clicked.connect(self.confirm_delete)
        self.save_btn.clicked.connect(self.save_drawing)
        self.undo_btn.clicked.connect(self.undo)
        self.redo_btn.clicked.connect(self.redo)
        self.camera_list.currentRowChanged.connect(self.show_camera_preview)
        
    def toggle_drawing_mode(self):
        """Toggle antara mode drawing dan normal"""
        self.is_drawing_enabled = self.toggle_drawing_btn.isChecked()
        
        # Update tombol toggle
        self.toggle_drawing_btn.setText(f"Mode Drawing: {'ON' if self.is_drawing_enabled else 'OFF'}")
        
        # Enable/disable tombol drawing
        self.border_btn.setEnabled(self.is_drawing_enabled)
        self.area_pred_btn.setEnabled(self.is_drawing_enabled)
        
        # Reset mode drawing jika dinonaktifkan
        if not self.is_drawing_enabled:
            self.drawing_mode = None
            self.current_points = []
            self.reset_button_styles()
            self.status_label.setText("Mode: Normal")
            self.status_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    padding: 5px;
                    color: white;
                    background-color: #333;
                    border-radius: 3px;
                }
            """)
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(0, 0, 0, 0.8);
                    color: white;
                    min-height: 600px;
                    min-width: 900px;
                    font-size: 24px;
                    border: 2px solid #34495e;
                    border-radius: 10px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            
            # Resume video
            for worker in self.video_workers:
                worker.paused = False
        
        # Update UI
        self.update_ui()
    
    def activate_border_tool(self):
        """Aktifkan tool untuk menggambar border"""
        self.reset_button_styles()
        self.border_btn.setStyleSheet(self.border_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        self.drawing_mode = 'border'
        self.current_points = []
        # Update status dan tampilan
        self.status_label.setText("Mode: Drawing Border")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 5px;
                color: white;
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        self.preview_label.setStyleSheet(self.preview_label.styleSheet().replace("border: 2px solid #ddd", "border: 2px solid #2ecc71"))
        # Pause video saat mode drawing aktif
        for worker in self.video_workers:
            worker.paused = True
    
    def activate_area_pred_tool(self):
        """Aktifkan tool untuk menggambar area prediksi"""
        self.reset_button_styles()
        self.area_pred_btn.setStyleSheet(self.area_pred_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        self.drawing_mode = 'area_pred'
        self.current_points = []
        # Update status dan tampilan
        self.status_label.setText("Mode: Drawing Area Prediction")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 5px;
                color: white;
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        self.preview_label.setStyleSheet(self.preview_label.styleSheet().replace("border: 2px solid #ddd", "border: 2px solid #3498db"))
        # Pause video saat mode drawing aktif
        for worker in self.video_workers:
            worker.paused = True
    
    def reset_button_styles(self):
        """Reset style semua tombol dan resume video"""
        # Gunakan style yang sama dengan yang didefinisikan di __init__
        button_style = """
            QPushButton {
                font-size: 14px;
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #3498db, stop:1 #2980b9);
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #2980b9, stop:1 #2472a4);
            }
            QPushButton:pressed {
                background: #2472a4;
            }
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #95a5a6, stop:1 #7f8c8d);
                color: #bdc3c7;
            }
        """
        
        # Terapkan style yang konsisten ke semua tombol
        for btn in [self.border_btn, self.area_pred_btn, self.delete_btn, self.save_btn, self.undo_btn, self.redo_btn]:
            btn.setStyleSheet(button_style)
        
        # Reset status dan tampilan
        self.status_label.setText("Mode: Normal")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                padding: 5px;
                color: white;
                background-color: #333;
                border-radius: 3px;
            }
        """)
        
        # Reset border style preview label dengan style yang konsisten
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                min-height: 600px;
                min-width: 900px;
                font-size: 24px;
                border: 2px solid #34495e;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        
        # Reset mode drawing dan resume video
        self.drawing_mode = None
        for worker in self.video_workers:
            worker.paused = False
    
    def confirm_delete(self):
        """Konfirmasi sebelum menghapus area"""
        from PyQt5.QtWidgets import QMessageBox
        if self.drawing_mode and (self.points[self.current_camera][self.drawing_mode] or self.current_points):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Apakah Anda yakin ingin menghapus area yang dipilih?")
            msg.setWindowTitle("Konfirmasi Hapus")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if msg.exec_() == QMessageBox.Yes:
                self.delete_selected()
    
    def delete_selected(self):
        """Hapus item yang dipilih"""
        if self.drawing_mode:
            # Simpan state sebelum menghapus
            self.save_state()
            self.points[self.current_camera][self.drawing_mode] = []
            self.current_points = []
            self.update_ui()
            self.update_undo_redo_buttons()
    
    def save_drawing(self):
        """Simpan hasil gambar ke config YAML dengan format yang lebih rapi"""
        from PyQt5.QtWidgets import QMessageBox
        config = load_config()
        
        # Restrukturisasi koordinat untuk format yang lebih rapi
        coordinates = {}
        for camera_id, areas in self.points.items():
            coordinates[str(camera_id)] = {
                'border': [[int(p[0]), int(p[1])] for p in areas['border']],
                'area_pred': [[int(p[0]), int(p[1])] for p in areas['area_pred']]
            }
        
        config['coordinates'] = coordinates
        
        # Gunakan ruang custom untuk koordinat
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True
        
        try:
            with open(config['config_path'], 'w') as f:
                yaml.dump(config, f, default_flow_style=None, sort_keys=False, Dumper=NoAliasDumper,
                         width=1000, indent=2)
                
            # Tampilkan notifikasi sukses
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Koordinat berhasil disimpan!")
            msg.setInformativeText(f"File tersimpan di:\n{config['config_path']}")
            msg.setWindowTitle("Sukses")
            msg.exec_()
            
        except Exception as e:
            # Tampilkan notifikasi error jika terjadi masalah
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Gagal menyimpan koordinat!")
            msg.setInformativeText(f"Error: {str(e)}")
            msg.setWindowTitle("Error")
            msg.exec_()

    def load_coordinates(self):
        """Muat koordinat dari config YAML"""
        config = load_config()
        
        if 'coordinates' in config:
            try:
                # Konversi string key ke integer
                self.points = {int(k): v for k, v in config['coordinates'].items()}
                print(f"Koordinat dimuat dari: {config['config_path']}")
            except (KeyError, ValueError) as e:
                print(f"Error saat memuat koordinat: {e}")

    def update_ui(self):
        """Update UI dengan frame terbaru dan gambar dengan optimasi"""
        if self.last_frames[self.current_camera] is not None:
            # Gunakan frame langsung tanpa copy untuk menghemat memori
            frame = self.last_frames[self.current_camera]
            
            # Buat frame baru hanya jika ada yang perlu digambar
            if (self.points[self.current_camera]['border'] or 
                self.points[self.current_camera]['area_pred'] or 
                self.current_points):
                frame = frame.copy()
                
                # Gambar titik-titik yang tersimpan
                if self.points[self.current_camera]['border']:
                    points = np.array(self.points[self.current_camera]['border'])
                    cv2.polylines(frame, [points], True, (0, 255, 0), 2)
                if self.points[self.current_camera]['area_pred']:
                    points = np.array(self.points[self.current_camera]['area_pred'])
                    cv2.polylines(frame, [points], True, (255, 0, 0), 2)
                
                # Gambar titik-titik yang sedang digambar
                if self.current_points:
                    color = (0, 255, 0) if self.drawing_mode == 'border' else (255, 0, 0)
                    points = np.array(self.current_points)
                    if len(points) > 0:
                        cv2.polylines(frame, [points], False, color, 2)
                        for point in points:
                            cv2.circle(frame, tuple(point), 3, color, -1)
            
            # Konversi frame ke QPixmap dengan optimasi
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Gunakan FastTransformation untuk performa lebih baik
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), 
                                        Qt.KeepAspectRatio, 
                                        Qt.FastTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            self.preview_label.clear()
            self.preview_label.setText(f"NO SIGNAL\nCamera CH{self.current_camera + 1}")
    
    def store_frame(self, frame, camera_id):
        """Simpan frame untuk diproses nanti dengan resolusi tetap 1280x720"""
        try:
            # Pastikan frame valid dan tidak None
            if frame is None:
                print(f"Warning: Received None frame from camera {camera_id}")
                return
            
            # Resize frame ke 1280x720
            frame_resized = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
            
            # Gunakan frame langsung tanpa copy untuk menghemat memori
            self.last_frames[camera_id] = frame_resized
            
            # Update UI jika frame ini dari kamera yang sedang aktif
            if camera_id == self.current_camera:
                self.update_ui()
                
            # Debug info saat pertama kali menerima frame
            if self.last_frames[camera_id] is None:
                print(f"First frame received from camera {camera_id}")
                
        except Exception as e:
            print(f"Error in store_frame for camera {camera_id}: {str(e)}")
            import traceback
            traceback.print_exc()

    def show_camera_preview(self, index):
        """Tampilkan preview kamera yang dipilih"""
        if self.current_camera != index:  # Hanya print saat benar-benar ganti kamera
            print(f"\nSwitching to camera {index}")
            print(f"Current frames status: CH1: {'Available' if self.last_frames[0] is not None else 'None'}, "
                  f"CH2: {'Available' if self.last_frames[1] is not None else 'None'}\n")
        self.current_camera = index
        self.update_ui()
    
    def closeEvent(self, event):
        """Bersihkan video workers dan simpan koordinat saat window ditutup"""
        self.update_timer.stop()
        # Resume semua video workers sebelum menutup window
        for worker in self.video_workers:
            worker.paused = False
        self.save_drawing()
        super().closeEvent(event)
    
    def save_state(self):
        """Simpan state saat ini ke undo stack"""
        current_state = {
            'points': {k: {t: v[t].copy() for t in v} for k, v in self.points.items()},
            'current_points': self.current_points.copy(),
            'camera': self.current_camera,
            'mode': self.drawing_mode
        }
        self.undo_stack.append(current_state)
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.update_undo_redo_buttons()
    
    def undo(self):
        """Kembalikan ke state sebelumnya"""
        if self.undo_stack:
            # Simpan state saat ini ke redo stack
            current_state = {
                'points': {k: {t: v[t].copy() for t in v} for k, v in self.points.items()},
                'current_points': self.current_points.copy(),
                'camera': self.current_camera,
                'mode': self.drawing_mode
            }
            self.redo_stack.append(current_state)
            
            # Kembalikan ke state sebelumnya
            prev_state = self.undo_stack.pop()
            self.points = prev_state['points']
            self.current_points = prev_state['current_points']
            if self.current_camera != prev_state['camera']:
                self.camera_list.setCurrentRow(prev_state['camera'])
            self.drawing_mode = prev_state['mode']
            
            self.update_ui()
            self.update_undo_redo_buttons()
    
    def redo(self):
        """Ulangi perubahan yang di-undo"""
        if self.redo_stack:
            # Simpan state saat ini ke undo stack
            current_state = {
                'points': {k: {t: v[t].copy() for t in v} for k, v in self.points.items()},
                'current_points': self.current_points.copy(),
                'camera': self.current_camera,
                'mode': self.drawing_mode
            }
            self.undo_stack.append(current_state)
            
            # Kembalikan ke state yang di-redo
            next_state = self.redo_stack.pop()
            self.points = next_state['points']
            self.current_points = next_state['current_points']
            if self.current_camera != next_state['camera']:
                self.camera_list.setCurrentRow(next_state['camera'])
            self.drawing_mode = next_state['mode']
            
            self.update_ui()
            self.update_undo_redo_buttons()
    
    def update_undo_redo_buttons(self):
        """Update status tombol undo/redo"""
        self.undo_btn.setEnabled(bool(self.undo_stack))
        self.redo_btn.setEnabled(bool(self.redo_stack))
    
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
            # Simpan state sebelum menambah titik
            if not self.current_points:  # Hanya simpan state saat mulai menggambar
                self.save_state()
            self.current_points.append([x, y])
            self.update_ui()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click untuk mengakhiri gambar"""
        if not self.drawing_mode or not self.current_points:
            return
            
        # Simpan state sebelum mengakhiri gambar
        self.save_state()
        # Simpan titik-titik ke points
        self.points[self.current_camera][self.drawing_mode] = self.current_points.copy()
        self.current_points = []
        self.update_ui()
        self.update_undo_redo_buttons()