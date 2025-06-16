# traker_deepSort.py
import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import torch

class DeepSortTracker:
    def __init__(self, model_path, max_age=30, n_init=3, nms_max_overlap=1.2, max_cosine_distance=0.3):
        self.model = YOLO(model_path)
        # print(f"Model loaded with classes: {self.model.names}")
        # print(f"Model parameters: {self.model.parameters}")
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            nms_max_overlap=nms_max_overlap,
            max_cosine_distance=max_cosine_distance
        )
        
        self.COLOR_MAP = {
            # "body": (0, 255, 0),          # Hijau
            "azko": (0, 0, 255),      
            "kawan_lama@ungu": (216, 191, 216),
            "kawan_lama@abu": (128, 128, 128),
            "informa": (230, 216, 173),
            "driver_informa": (173, 216, 230),
            "distribution_center": (139, 0, 0),
            "service_center": (0, 0, 128),
            "cipta_selera": (255, 255, 153),
            "elite": (85, 107, 47),
            "non_uniform": (57, 255, 20),
            "kawan_lama@driver": (0, 0, 139)
        }
        
    def check_intersection_with_line(self, bbox, line_points):
        if not line_points or len(line_points) < 2:
            return False
            
        bbox_bottom_center = [
            (bbox[0] + bbox[2]) // 2,
            bbox[3]
        ]
        
        for i in range(len(line_points) - 1):
            p1 = line_points[i]
            p2 = line_points[i + 1]
            
            d1 = self._direction(p1, p2, bbox_bottom_center)
            if d1 == 0:
                return True
                
            if (p1[1] <= bbox_bottom_center[1] <= p2[1] or 
                p2[1] <= bbox_bottom_center[1] <= p1[1]):
                if (p1[0] <= bbox_bottom_center[0] <= p2[0] or 
                    p2[0] <= bbox_bottom_center[0] <= p1[0]):
                    return True
                    
        return False
        
    def _direction(self, p1, p2, p3):
        return ((p2[0] - p1[0]) * (p3[1] - p1[1])) - ((p2[1] - p1[1]) * (p3[0] - p1[0]))

    def update(self, frame, class_names=None):
        results = self.model.predict(frame, device='cuda' if torch.cuda.is_available() else 'cpu', verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                cls = int(box.cls[0].item())
                # print([int(box.cls[0].item()) for r in results for box in r.boxes])
                
                if conf > 0.3: #threshold confidence
                    class_name = class_names[cls] if class_names and cls in class_names else str(cls)
                    detections.append(([x1, y1, x2-x1, y2-y1], conf, class_name))
                    # print(f"Added detection: {class_name} with conf {conf:.4f}")

        tracks = self.tracker.update_tracks(detections, frame=frame)
        # Assign confidence ke track
        for track in tracks:
            if track.is_confirmed():
                # Cari detection yang sesuai
                for det in detections:
                    if track.det_class == det[2]:  # Match class name
                        track.confidence = det[1]  # Assign confidence
                    break

        return tracks, detections

    def draw_tracks(self, frame, tracks, draw_trail=False):
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            bbox = track.to_ltrb()
            class_name = track.det_class if hasattr(track, 'det_class') else "unknown"
            # confidence = getattr(track, 'confidence', 0.0)
            
            color = self.COLOR_MAP.get(class_name, (0, 255, 0))
            
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{class_name} ID:{track_id}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x1, y1-20), (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            
            if draw_trail and hasattr(track, 'centroidarr'):
                points = track.centroidarr
                for i in range(1, len(points)):
                    if points[i-1] is None or points[i] is None:
                        continue
                    cv2.line(frame, tuple(map(int, points[i-1])), 
                            tuple(map(int, points[i])), color, 2)
                            
        return frame