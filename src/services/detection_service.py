from ultralytics import YOLO
import cv2
import torch
import numpy as np

class DetectionService:
    def __init__(self, model_path):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
        self.tracked_objects = {}  # Untuk menyimpan status objek yang ditrack

    def load_model(self):
        """Memuat model YOLOv8 dari file .pt"""
        try:
            self.model = YOLO(self.model_path)
            print("Model YOLOv8 berhasil dimuat")
        except Exception as e:
            print(f"Gagal memuat model: {str(e)}")
            self.model = None
            
    def check_intersection_with_line(self, point_x, point_y, line_points):
        """Mengecek apakah titik berpotongan dengan garis poligon"""
        intersections = 0
        n = len(line_points)
        
        for i in range(n):
            j = (i + 1) % n
            if ((line_points[i][1] > point_y) != (line_points[j][1] > point_y) and
                point_x < (line_points[j][0] - line_points[i][0]) * (point_y - line_points[i][1]) /
                          (line_points[j][1] - line_points[i][1]) + line_points[i][0]):
                intersections += 1
        
        return intersections % 2 == 1

    def detect(self, frame, camera_id, border_points=None, area_pred_points=None):
        """Melakukan deteksi pada frame menggunakan YOLOv8 dengan pengecekan border dan area prediksi"""
        if self.model is None:
            return frame, []

        # YOLOv8 expects BGR image (OpenCV default)
        results = self.model.predict(frame, device=str(self.device), verbose=False)
        detections = []
        current_frame_objects = set()  # Untuk tracking objek di frame saat ini

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                cls = int(box.cls[0].item())
                
                # Hitung titik tengah bounding box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Generate ID unik untuk objek
                object_id = f"{camera_id}_{x1}_{y1}_{x2}_{y2}"
                current_frame_objects.add(object_id)
                
                # Inisialisasi status objek jika belum ada
                if object_id not in self.tracked_objects:
                    self.tracked_objects[object_id] = {
                        'crossed_border': False,
                        'crossed_area_pred': False,
                        'class': cls,
                        'recognition_id': None
                    }
                
                # Cek interseksi dengan border
                if border_points and len(border_points) > 1:
                    if not self.tracked_objects[object_id]['crossed_border']:
                        if self.check_intersection_with_line(center_x, center_y, border_points):
                            self.tracked_objects[object_id]['crossed_border'] = True
                            # Di sini akan dilakukan recognition saat objek melewati border
                            self.tracked_objects[object_id]['recognition_id'] = f"Seragam_{cls}"
                
                # Cek interseksi dengan area prediksi
                if area_pred_points and len(area_pred_points) > 1:
                    if not self.tracked_objects[object_id]['crossed_area_pred']:
                        if self.check_intersection_with_line(center_x, center_y, area_pred_points):
                            self.tracked_objects[object_id]['crossed_area_pred'] = True
                
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class': cls,
                    'object_id': object_id,
                    'recognition_id': self.tracked_objects[object_id]['recognition_id'] if self.tracked_objects[object_id]['crossed_area_pred'] else None
                })
        
        # Bersihkan objek yang tidak terdeteksi lagi
        self.tracked_objects = {k: v for k, v in self.tracked_objects.items() if k in current_frame_objects}
        
        annotated_frame = self.draw_detections(frame.copy(), detections)
        return annotated_frame, detections

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame dengan ID recognition"""
        for det in detections:
            bbox = det['bbox']
            conf = det['confidence']
            recognition_id = det.get('recognition_id')
            
            # Gambar bounding box
            color = (0, 255, 0) if recognition_id else (255, 0, 0)
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Tambahkan label confidence dan recognition ID jika ada
            label = f"{conf:.2f}"
            if recognition_id:
                label += f" | {recognition_id}"
            cv2.putText(frame, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
        return frame