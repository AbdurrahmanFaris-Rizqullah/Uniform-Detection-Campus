# Digunakan untuk mengelola koneksi kamera dan mengelola frame yang diterima dari kamera. Sehingga dapat diakses oleh window utama, dan masih dapat mendeteksi walau di close.

from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import time
from src.utils.config import load_config
from src.services.detection_service import DetectionService

class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)
    
    def __init__(self, camera_config, camera_id):
        super().__init__()
        self.source = camera_config['source']
        self.resolution = camera_config['resolution']
        self.fps = camera_config['fps']
        self.camera_id = camera_id
        self.running = True
        self.paused = False
        
        # Inisialisasi model deteksi
        self.detector = DetectionService('D:\\1-kerja-2025\\uniform-detection\\models\\best.pt')
        # Kurangi FPS untuk menghemat CPU
        target_fps = min(15, self.fps if self.fps > 0 else 30)  # Batasi maksimum 15 FPS
        self.frame_interval = 1.0 / target_fps
        self.last_frame_time = 0
        self.last_frame = None  # Menyimpan frame terakhir untuk mode pause
        self.frame_skip = 2  # Skip setiap 2 frame untuk menghemat CPU
        
    def run(self):
        print(f"Menghubungkan kamera {self.camera_id + 1}...")
        cap = cv2.VideoCapture(self.source)
        
        # Cek apakah kamera berhasil dibuka
        if not cap.isOpened():
            print(f"\033[31m[Kamera {self.camera_id + 1}] Tidak terhubung\033[0m")
            return
            
        # Setup properti kamera
        if self.fps > 0:
            cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        
        # Verifikasi properti kamera
        actual_fps = cap.get(cv2.CAP_PROP_FPS)
        actual_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"Kamera {self.camera_id + 1} terhubung")
        
        frame_count = 0
        connection_attempts = 0
        max_attempts = 3
        
        while self.running:
            if self.paused:
                if self.last_frame is not None:
                    self.frame_ready.emit(self.last_frame, self.camera_id)
                time.sleep(0.1)  # Kurangi penggunaan CPU saat pause
                continue
                
            current_time = time.time()
            # Baca frame tapi skip beberapa untuk menghemat CPU
            ret, frame = cap.read()
            frame_count += 1
            
            if not ret:
                connection_attempts += 1
                print(f"Mencoba menghubungkan ulang kamera {self.camera_id + 1}")
                
                if connection_attempts >= max_attempts:
                    print(f"Kamera {self.camera_id + 1} terputus")
                    break
                    
                # Coba tutup dan buka ulang kamera
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(self.source)
                
                if not cap.isOpened():
                    print(f"\033[31m[Kamera {self.camera_id + 1}] Tidak terhubung\033[0m")
                    break
                    
                frame_count = 0
                continue
                
            # Reset counter jika berhasil membaca frame
            connection_attempts = 0
                
            # Skip frame untuk menghemat CPU
            if frame_count % self.frame_skip != 0:
                continue
                
            # Hanya proses frame jika sudah waktunya
            if current_time - self.last_frame_time >= self.frame_interval:
                # Resize frame dengan ukuran yang lebih kecil
                if frame.shape[1] > 960:  # Kurangi ukuran maksimum ke 960
                    scale = 960.0 / frame.shape[1]
                    frame = cv2.resize(frame, None, fx=scale, fy=scale,
                                     interpolation=cv2.INTER_AREA)
                
                # Load koordinat dari config
                config = load_config()
                border_points = []
                area_pred_points = []
                if 'coordinates' in config and str(self.camera_id) in config['coordinates']:
                    camera_coords = config['coordinates'][str(self.camera_id)]
                    border_points = camera_coords.get('border', [])
                    area_pred_points = camera_coords.get('area_pred', [])
                
                # Lakukan deteksi pada frame dengan koordinat border dan area prediksi
                detected_frame, detections = self.detector.detect(
                    frame,
                    self.camera_id,
                    border_points,
                    area_pred_points
                )
                self.last_frame = detected_frame
                self.frame_ready.emit(detected_frame, self.camera_id)
                self.last_frame_time = current_time
            
            # Tidur lebih lama untuk mengurangi penggunaan CPU
            time.sleep(0.01)
        
        cap.release()
        
    def stop(self):
        self.running = False

def create_video_workers():
    """Buat video workers untuk semua kamera"""
    video_workers = []
    config = load_config()
    
    for i in range(1, 3):  # Untuk kamera 1 dan 2
        camera_config = config['cameras'][f'camera_{i}']
        worker = VideoWorker(camera_config, i-1)  # i-1 untuk index 0-based
        worker.start()
        video_workers.append(worker)
    
    return video_workers