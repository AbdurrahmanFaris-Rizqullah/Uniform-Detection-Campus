from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGraphicsView, QGraphicsScene,
                            QListWidget, QFrame)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drawing Detection Area")
        self.setGeometry(200, 200, 1280, 720)
        
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