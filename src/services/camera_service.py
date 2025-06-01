from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import time
from src.utils.config import load_config
from src.services.traker_deepSort import DeepSortTracker  # Ganti import sesuai proyekmu

class VideoWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)
    update_counter = pyqtSignal(str)
    
    def __init__(self, camera_config, camera_id):
        super().__init__()
        self.source = camera_config['source']
        self.resolution = camera_config['resolution']
        self.camera_id = camera_id
        self.running = True
        self.paused = False
         
        # Class names untuk model deteksi
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
        
        # Inisialisasi tracker DeepSort
        self.tracker = DeepSortTracker(
            model_path='D:\\1-kerja-2025\\uniform-detection\\models\\best.pt',
            max_age=10,
            n_init=1,
            nms_max_overlap=0.5
        )
        
        # Set ini ke 1 supaya tidak skip frame (proses semua frame)
        self.frame_skip = 1
        self.counted_tracks = set()
        self.performance_stats = {
        'frame_times': [],
        'start_time': None,
        'frame_count': 0
       }

    def detect_and_track(self, frame, border_points=None, area_pred_points=None):
        """Deteksi dan tracking objek dengan DeepSORT"""
        # Resize ke 800x600 jika frame tidak sesuai
        frame_height, frame_width = frame.shape[:2]
        if frame_width != 800 or frame_height != 600:
            frame = cv2.resize(frame, (800, 600), interpolation=cv2.INTER_LINEAR)
            frame_height, frame_width = 600, 800
        
        # Scale koordinat dari 1280x720 ke 800x600
        if area_pred_points:
            scaled_area_pred = []
            for point in area_pred_points:
                # Scaling dari koordinat asli ke 800x600
                x = int(point[0] * (800 / 1280))
                y = int(point[1] * (600 / 720))
                scaled_area_pred.append([x, y])
            area_pred_points = scaled_area_pred

        if border_points:
            scaled_border = []
            for point in border_points:
                x = int(point[0] * (800 / 1280))
                y = int(point[1] * (600 / 720))
                scaled_border.append([x, y])
            border_points = scaled_border

        # Debug untuk memastikan scaling bekerja
        # print(f"Frame shape: {frame.shape}")
        # print(f"Scaled area pred points: {area_pred_points}")
        # print(f"Scaled border points: {border_points}")

        tracks, detections = self.tracker.update(frame, self.class_names)
        tracked_detections = []

        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            bbox = track.to_ltrb()
            class_name = track.det_class if hasattr(track, 'det_class') else "unknown"
            x1, y1, x2, y2 = map(int, bbox)

            # Debug tracking
            # print(f"Track ID: {track_id}, Class: {class_name}, BBox: {[x1,y1,x2,y2]}")

            if area_pred_points:
                is_crossing_pred = self.tracker.check_intersection_with_line([x1, y1, x2, y2], area_pred_points)
                # print(f"Checking intersection for track {track_id}:")
                # print(f"BBox points: {[x1,y1,x2,y2]}")
                # print(f"Area pred points: {area_pred_points}")
                # print(f"Is crossing: {is_crossing_pred}")
                
                if is_crossing_pred and track_id not in self.counted_tracks:
                    # print(f"Adding track {track_id} to counted_tracks")
                    self.counted_tracks.add(track_id)
                    # print(f"Emitting counter update for class {class_name}")
                    self.update_counter.emit(class_name)
                    tracked_detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'object_id': track_id,
                        'display_label': f"{class_name} | ID_{track_id}"
                    })

        annotated_frame = self.tracker.draw_tracks(frame.copy(), tracks)
        return annotated_frame, tracked_detections
        
    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame"""
        for det in detections:
            bbox = det['bbox']
            display_label = det['display_label']
            
            color = (0, 255, 0)  # Warna hijau
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
            
        # Dapatkan FPS dari video source
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        if original_fps <= 0:
            original_fps = 10
        
        frame_interval = 1.0 / original_fps
        print(f"Video FPS: {original_fps}")
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        print(f"Kamera {self.camera_id + 1} terhubung")
        
        frame_count = 0
        connection_attempts = 0
        max_attempts = 3
        start_time = time.time()
        
        while self.running:
            if self.paused:
                if self.last_frame is not None:
                    self.frame_ready.emit(self.last_frame, self.camera_id)
                time.sleep(0.1)
                continue
                
            # Hitung waktu yang seharusnya untuk frame ini
            target_time = start_time + (frame_count * frame_interval)
            current_time = time.time()
            
            # Tunggu sampai waktu yang tepat
            if current_time < target_time:
                time.sleep(target_time - current_time)
                
            ret, frame = cap.read()
            
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
                start_time = time.time()
                continue
                
            connection_attempts = 0
            
            # Resize frame jika terlalu besar
            if frame.shape[1] > 960:
                scale = 960.0 / frame.shape[1]
                frame = cv2.resize(frame, None, fx=scale, fy=scale,
                                interpolation=cv2.INTER_LINEAR)
            
            # Process frame
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
            
            frame_count += 1
            
            # Debug: print actual FPS setiap 30 frame
            if frame_count % 30 == 0:
                current_time = time.time()
                elapsed_total = current_time - start_time
                actual_fps = frame_count / elapsed_total
                # print(f"Camera {self.camera_id + 1} - Target FPS: {original_fps:.2f}, Actual FPS: {actual_fps:.2f}")
    
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
