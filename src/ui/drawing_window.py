from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGraphicsView, QGraphicsScene,
                            QListWidget, QFrame)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deteksi Seragam")
        self.setGeometry(200, 200, 1280, 720)
        
        # Widget dan layout utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)  # Ubah ke horizontal untuk split view
        
        # Layout kiri untuk drawing area
        left_layout = QVBoxLayout()
        
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
        
        # Area gambar utama
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene.setSceneRect(QRectF(0, 0, 800, 600))
        
        # Tambahkan ke layout kiri
        left_layout.addLayout(toolbar_layout)
        left_layout.addWidget(self.view)
        
        # Layout kanan untuk preview dan list kamera
        right_layout = QVBoxLayout()
        
        # Preview area
        self.preview_label = QLabel("Preview")
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: white;
                min-height: 400px;
                font-size: 24px;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        
        # List kamera
        self.camera_list = QListWidget()
        self.camera_list.addItems(["Cam CH1", "Cam CH2"])
        self.camera_list.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                min-height: 150px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
            }
        """)
        
        # Tambahkan ke layout kanan
        right_layout.addWidget(self.preview_label)
        right_layout.addWidget(self.camera_list)
        
        # Tambahkan layout kiri dan kanan ke main layout
        main_layout.addLayout(left_layout, stretch=2)  # Proporsi 2
        main_layout.addLayout(right_layout, stretch=1)  # Proporsi 1
        
        # Setup tools
        self.setup_tools()
        
    def setup_tools(self):
        """Setup event handlers dan tools"""
        self.border_btn.clicked.connect(self.activate_border_tool)
        self.area_pred_btn.clicked.connect(self.activate_area_pred_tool)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.save_btn.clicked.connect(self.save_drawing)
        self.camera_list.itemClicked.connect(self.show_camera_preview)
    
    def activate_border_tool(self):
        """Aktifkan tool untuk menggambar border"""
        self.border_btn.setStyleSheet(self.border_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        # TODO: Implementasi drawing mode
    
    def activate_area_pred_tool(self):
        """Aktifkan tool untuk menggambar area prediksi"""
        self.area_pred_btn.setStyleSheet(self.area_pred_btn.styleSheet() + "QPushButton { background-color: #c0c0c0; }")
        # TODO: Implementasi drawing mode
    
    def delete_selected(self):
        """Hapus item yang dipilih"""
        # TODO: Implementasi delete
        pass
    
    def save_drawing(self):
        """Simpan hasil gambar"""
        # TODO: Implementasi save
        pass
    
    def show_camera_preview(self, item):
        """Tampilkan preview kamera yang dipilih"""
        # TODO: Implementasi preview kamera
        self.preview_label.setText(f"Preview: {item.text()}")