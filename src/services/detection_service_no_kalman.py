from ultralytics import YOLO
import cv2
import torch
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from traker.traker_no_kalman import CentroidTracker

class DetectionServiceNoKalman(QObject):
    update_counter = pyqtSignal(str)
    
    def __init__(self, model_path):
        super().__init__()
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
        self.tracker = CentroidTracker(max_disappeared=10)
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
        self.counted_tracks = set()

    def load_model(self):
        """Memuat model YOLOv8 dari file .pt"""
        try:
            self.model = YOLO(self.model_path)
            print("Model YOLOv8 berhasil dimuat")
        except Exception as e:
            print(f"Gagal memuat model: {str(e)}")
            self.model = None
            
    def check_intersection_with_line(self, bbox, line_points):
        """Mengecek apakah bounding box berpotongan dengan garis border/prediksi"""
        if len(line_points) < 2:
            return False
            
        x1, y1, x2, y2 = bbox
        box_points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
        
        for i in range(len(box_points)):
            box_p1 = box_points[i]
            box_p2 = box_points[(i + 1) % 4]
            
            for j in range(len(line_points) - 1):
                line_p1 = line_points[j]
                line_p2 = line_points[j + 1]
                
                if self.line_segments_intersect(box_p1, box_p2, line_p1, line_p2):
                    return True
                    
        return False
        
    def line_segments_intersect(self, p1, p2, p3, p4):
        """Mengecek apakah dua segmen garis berpotongan"""
        def ccw(A, B, C):
            return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
            
        return ccw(p1,p3,p4) != ccw(p2,p3,p4) and ccw(p1,p2,p3) != ccw(p1,p2,p4)

    def detect(self, frame, camera_id, border_points=None, area_pred_points=None):
        if self.model is None:
            return frame, []

        results = self.model.predict(frame, device=str(self.device), verbose=False)
        detections = []
        
        rects = []
        class_names = []
    
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                cls = int(box.cls[0].item())
                
                if conf > 0.5:  # Tambahkan threshold confidence
                    class_name = self.class_names[cls]
                    rects.append([x1, y1, x2, y2])
                    class_names.append(class_name)

        # Update tracker dengan rects dan class_names
        tracked_objects = self.tracker.update(rects, class_names)
        
        # Proses hasil tracking
        for object_id, obj_info in tracked_objects.items():
            bbox = obj_info["bbox"]
            class_name = obj_info["class_name"]
            x1, y1, x2, y2 = bbox
            
            # Cek interseksi dengan border
            if border_points:
                is_crossing_border = self.check_intersection_with_line([x1, y1, x2, y2], border_points)
                if is_crossing_border:
                    display_label = f"{class_name}"
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'object_id': object_id,
                        'display_label': display_label
                    })
            
            # Cek interseksi dengan area prediksi
            if area_pred_points:
                is_crossing_pred = self.check_intersection_with_line([x1, y1, x2, y2], area_pred_points)
                if is_crossing_pred and object_id not in self.counted_tracks:
                    self.counted_tracks.add(object_id)
                    self.update_counter.emit(class_name)
                    
                    display_label = f"{class_name} | ID_{object_id}"
                    detections.append({
                        'bbox': [x1, y1, x2, y2],
                        'class': class_name,
                        'object_id': object_id,
                        'display_label': display_label
                    })

        annotated_frame = self.draw_detections(frame.copy(), detections)
        return annotated_frame, detections

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame dengan label yang sesuai"""
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