from ultralytics import YOLO
import cv2
import torch
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal

class DetectionService(QObject):  # Inherit dari QObject untuk menggunakan signal
    update_counter = pyqtSignal(str)  # Signal untuk update counter
    
    def __init__(self, model_path):
        super().__init__()  # Inisialisasi parent class QObject
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
        self.tracked_objects = {}
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
            9: "non_uniform"
        }

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
            
        # Dapatkan titik-titik bounding box
        x1, y1, x2, y2 = bbox
        box_points = [(x1,y1), (x2,y1), (x2,y2), (x1,y2)]
        
        # Cek setiap sisi bounding box dengan setiap segmen garis
        for i in range(len(box_points)):
            box_p1 = box_points[i]
            box_p2 = box_points[(i + 1) % 4]
            
            for j in range(len(line_points) - 1):
                line_p1 = line_points[j]
                line_p2 = line_points[j + 1]
                
                # Cek perpotongan antara dua segmen garis
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
        current_frame_objects = set()
    
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                cls = int(box.cls[0].item())
                class_name = self.class_names[cls]
                
                # Generate ID unik untuk objek yang lebih stabil
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                object_id = f"{camera_id}_{cls}_{center_x}_{center_y}"
                current_frame_objects.add(object_id)
                
                # Inisialisasi status objek jika belum ada
                if object_id not in self.tracked_objects:
                    self.tracked_objects[object_id] = {
                        'class': class_name,
                        'crossed_border': False,
                        'crossed_area_pred': False,
                        'recognition_id': None,
                        'counted': False
                    }
                
                # Cek interseksi dengan border
                if border_points:
                    is_crossing_border = self.check_intersection_with_line([x1, y1, x2, y2], border_points)
                    if is_crossing_border:
                        self.tracked_objects[object_id]['crossed_border'] = True
                        display_label = f"{class_name} | {conf:.2f}"
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': conf,
                            'class': class_name,
                            'object_id': object_id,
                            'display_label': display_label
                        })
                
                # Cek interseksi dengan area prediksi
                if area_pred_points:
                    is_crossing_pred = self.check_intersection_with_line([x1, y1, x2, y2], area_pred_points)
                    if is_crossing_pred and not self.tracked_objects[object_id]['crossed_area_pred']:
                        self.tracked_objects[object_id]['crossed_area_pred'] = True
                        self.tracked_objects[object_id]['recognition_id'] = f"ID_{len(self.tracked_objects)}"
                        
                        # Update counter jika belum dihitung
                        if not self.tracked_objects[object_id]['counted']:
                            self.tracked_objects[object_id]['counted'] = True
                            self.update_counter.emit(class_name)  # Emit signal untuk update counter
                            
                        # Update label dengan ID
                        display_label = f"{class_name} | {conf:.2f} | {self.tracked_objects[object_id]['recognition_id']}"
                        detections.append({
                            'bbox': [x1, y1, x2, y2],
                            'confidence': conf,
                            'class': class_name,
                            'object_id': object_id,
                            'display_label': display_label
                        })

        # Bersihkan objek yang tidak terdeteksi lagi
        self.tracked_objects = {k: v for k, v in self.tracked_objects.items() if k in current_frame_objects}
        
        annotated_frame = self.draw_detections(frame.copy(), detections)
        return annotated_frame, detections

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame dengan label yang sesuai"""
        for det in detections:
            bbox = det['bbox']
            display_label = det['display_label']
            
            # Gambar bounding box dengan warna yang sesuai
            color = (0, 255, 0)  # Hijau untuk semua deteksi yang sudah melewati border
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            
            # Tambahkan label dengan background hitam untuk keterbacaan
            label_size = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (bbox[0], bbox[1]-20), (bbox[0] + label_size[0], bbox[1]), color, -1)
            cv2.putText(frame, display_label, (bbox[0], bbox[1]-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return frame