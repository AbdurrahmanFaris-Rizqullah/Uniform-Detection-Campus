from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import time
from src.utils.config import load_config
from src.services.traker_deepSort import DeepSortTracker  # Ganti import

class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)
    update_counter = pyqtSignal(str)
    
    def __init__(self, camera_config, camera_id):
        super().__init__()
        self.source = camera_config['source']
        self.resolution = camera_config['resolution']
        self.fps = camera_config['fps']
        self.camera_id = camera_id
        self.running = True
        self.paused = False
        
        # Class names untuk model
        self.class_names = {
            0: "azko",
            1: "kawan_lama@ungu",
            2: "kawan_lama@abu",
            3: "informa",
            4: "driver_informa",
            5: "distribution_center",
            6: "service_center",
            7: "cipta_selera",
            8: "elite",
            9: "non_uniform",
            10: "kawan_lama@driver"
        }
        
        # Inisialisasi tracker
        self.tracker = DeepSortTracker(
            model_path='D:\\1-kerja-2025\\uniform-detection\\models\\best.pt',
            max_age=10,
            n_init=1,
            nms_max_overlap=0.5
        )
        
        # Kurangi FPS untuk menghemat CPU
        target_fps = min(60, self.fps if self.fps > 0 else 30)
        self.frame_interval = 1.0 / target_fps
        self.last_frame_time = 0
        self.last_frame = None
        self.frame_skip = 1
        self.counted_tracks = set()

    def detect_and_track(self, frame, border_points=None, area_pred_points=None):
        """Deteksi dan tracking objek dengan DeepSORT"""
        # Update tracker dengan frame baru
        tracks, detections = self.tracker.update(frame, self.class_names)
        tracked_detections = []

        # Proses hasil tracking
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            bbox = track.to_ltrb()
            class_name = track.det_class if hasattr(track, 'det_class') else "unknown"
            x1, y1, x2, y2 = map(int, bbox)

            # Cek interseksi dengan border dan area prediksi
            if border_points:
                is_crossing_border = self.tracker.check_intersection_with_line([x1, y1, x2, y2], border_points)
                if is_crossing_border:
                    tracked_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'object_id': track_id,
                        'display_label': f"{class_name}"
                    })

            if area_pred_points:
                is_crossing_pred = self.tracker.check_intersection_with_line([x1, y1, x2, y2], area_pred_points)
                if is_crossing_pred and track_id not in self.counted_tracks:
                    self.counted_tracks.add(track_id)
                    self.update_counter.emit(class_name)
                    tracked_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'object_id': track_id,
                        'display_label': f"{class_name} | ID_{track_id}"
                    })

        # Gambar hasil deteksi
        annotated_frame = self.tracker.draw_tracks(frame.copy(), tracks)
        return annotated_frame, tracked_detections

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame"""
        for det in detections:
            bbox = det['bbox']
            display_label = det['display_label']
            
            color = (0, 255, 0)  # Hijau untuk semua deteksi
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            label_size = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (bbox[0], bbox[1]-20), (bbox[0] + label_size[0], bbox[1]), color, -1)
            cv2.putText(frame, display_label, (bbox[0], bbox[1]-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame

    def run(self):
        print(f"Menghubungkan kamera {self.camera_id + 1}...")
        cap = cv2.VideoCapture(self.source)
        
        if not cap.isOpened():
            print(f"\033[31m[Kamera {self.camera_id + 1}] Tidak terhubung\033[0m")
            return
            
        if self.fps > 0:
            cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        print(f"Kamera {self.camera_id + 1} terhubung")
        
        frame_count = 0
        connection_attempts = 0
        max_attempts = 3
        
        while self.running:
            if self.paused:
                if self.last_frame is not None:
                    self.frame_ready.emit(self.last_frame, self.camera_id)
                time.sleep(0.1)
                continue
                
            ret, frame = cap.read()
            frame_count += 1
            
            if not ret:
                connection_attempts += 1
                print(f"Mencoba menghubungkan ulang kamera {self.camera_id + 1}")
                
                if connection_attempts >= max_attempts:
                    print(f"Kamera {self.camera_id + 1} terputus")
                    break
                    
                cap.release()
                time.sleep(1)
                cap = cv2.VideoCapture(self.source)
                
                if not cap.isOpened():
                    print(f"\033[31m[Kamera {self.camera_id + 1}] Tidak terhubung\033[0m")
                    break
                    
                frame_count = 0
                continue
                
            connection_attempts = 0
                
            if frame_count % self.frame_skip != 0:
                continue
                
            current_time = time.time()
            if current_time - self.last_frame_time >= self.frame_interval:
                if frame.shape[1] > 960:
                    scale = 960.0 / frame.shape[1]
                    frame = cv2.resize(frame, None, fx=scale, fy=scale,
                                     interpolation=cv2.INTER_LINEAR)
                
                config = load_config()
                border_points = []
                area_pred_points = []
                if 'coordinates' in config and str(self.camera_id) in config['coordinates']:
                    camera_coords = config['coordinates'][str(self.camera_id)]
                    border_points = camera_coords.get('border', [])
                    area_pred_points = camera_coords.get('area_pred', [])
                
                detected_frame, detections = self.detect_and_track(
                    frame,
                    border_points,
                    area_pred_points
                )
                
                self.last_frame = detected_frame
                self.frame_ready.emit(detected_frame, self.camera_id)
                self.last_frame_time = current_time
            
            time.sleep(0.04)
        
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
