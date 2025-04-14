from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt

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
        
        # Counter NON-UNIFORM (perbaiki urutan)
        counter_right = QVBoxLayout()
        counter_right.setSpacing(5)
        
        self.non_uniform_label = QLabel("NON-UNIFORM")
        self.non_uniform_label.setStyleSheet("QLabel { color: red; font-size: 24px; font-weight: bold; }")
        self.non_uniform_label.setFixedWidth(220)
        self.non_uniform_label.setAlignment(Qt.AlignCenter)
        
        self.non_uniform_count = QLabel("0")
        self.non_uniform_count.setStyleSheet("QLabel { font-size: 32px; font-weight: bold; }")
        self.non_uniform_count.setAlignment(Qt.AlignCenter)
        
        counter_right.addWidget(self.non_uniform_label)
        counter_right.addWidget(self.non_uniform_count)
        
        counter_layout.addLayout(counter_left)
        
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
        
        counter_layout.addLayout(counter_right)
        
        # Tambah stretch di akhir untuk menyeimbangkan
        counter_layout.addStretch()
        
        # Layout Seragam counter dengan spacing yang lebih rapi
        seragam_layout = QHBoxLayout()  # Ubah ke HBoxLayout untuk satu baris
        seragam_layout.setSpacing(50)   # Jarak antar item
        
        # List seragam dari hasil anotasi
        jenis_seragam = [
            "Azko", "Informa", "Driver_Informa", "kawan_lama@ungu", "kawan_lama@abu",
            "Distribution Center", "Service Center", "Cipta selera", "elite"
        ]
        
        # Tambahkan seragam dalam satu baris
        for seragam in jenis_seragam:
            label = QLabel(f"{seragam}\n0")
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("QLabel { font-size: 14px; padding: 5px; }")  # Font lebih kecil
            label.setFixedWidth(160)      # Lebar lebih kecil
            self.seragam_counters[seragam] = label
            seragam_layout.addWidget(label)
        
        # Menambahkan semua layout ke main layout
        main_layout.addLayout(cameras_layout)
        main_layout.addLayout(counter_layout)
        main_layout.addLayout(seragam_layout)
