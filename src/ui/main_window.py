from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton)
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Deteksi Seragam")
        self.setGeometry(100, 100, 1200, 600)
        
        # Widget utama
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Layout kiri (preview kamera)
        left_layout = QVBoxLayout()
        self.camera_label = QLabel("Preview Kamera")
        self.camera_label.setStyleSheet("QLabel { background-color: black; color: white; }")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(640, 480)
        left_layout.addWidget(self.camera_label)
        
        # Layout kanan (counter dan kontrol)
        right_layout = QVBoxLayout()
        
        # Counter seragam
        self.uniform_count = QLabel("UNIFORM\n0")
        self.uniform_count.setStyleSheet("QLabel { font-size: 24px; }")
        self.uniform_count.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.uniform_count)
        
        # Counter non-seragam
        self.non_uniform_count = QLabel("NON-UNIFORM\n0")
        self.non_uniform_count.setStyleSheet("QLabel { font-size: 24px; }")
        self.non_uniform_count.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.non_uniform_count)
        
        # Tombol kontrol
        self.start_button = QPushButton("Mulai Kamera")
        self.draw_line_button = QPushButton("Gambar Garis")
        self.settings_button = QPushButton("Pengaturan")
        
        right_layout.addWidget(self.start_button)
        right_layout.addWidget(self.draw_line_button)
        right_layout.addWidget(self.settings_button)
        
        # Menambahkan layout ke layout utama
        main_layout.addLayout(left_layout, stretch=2)
        main_layout.addLayout(right_layout, stretch=1)