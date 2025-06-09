from ultralytics import YOLO
import cv2

model = YOLO('best.pt')
img = cv2.imread('test1.png')
results = model(img)
for r in results:
    for box in r.boxes:
        cls = int(box.cls[0].item())
        print(cls)  # Harusnya ada angka 1 kalau 'body' terdeteksi