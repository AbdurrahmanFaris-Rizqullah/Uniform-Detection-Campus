from ultralytics import YOLO
import cv2
import torch

class DetectionService:
    def __init__(self, model_path):
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()

    def load_model(self):
        """Memuat model YOLOv8 dari file .pt"""
        try:
            self.model = YOLO(self.model_path)
            print("Model YOLOv8 berhasil dimuat")
        except Exception as e:
            print(f"Gagal memuat model: {str(e)}")
            self.model = None

    def detect(self, frame):
        """Melakukan deteksi pada frame menggunakan YOLOv8"""
        if self.model is None:
            return frame, []
        # YOLOv8 expects BGR image (OpenCV default)
        results = self.model.predict(frame, device=str(self.device), verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = float(box.conf[0].item())
                cls = int(box.cls[0].item())
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class': cls
                })
        annotated_frame = self.draw_detections(frame.copy(), detections)
        return annotated_frame, detections

    def draw_detections(self, frame, detections):
        """Menggambar hasil deteksi pada frame"""
        for det in detections:
            bbox = det['bbox']
            conf = det['confidence']
            # Gambar bounding box
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            # Tambahkan label confidence
            label = f"{conf:.2f}"
            cv2.putText(frame, label, (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame