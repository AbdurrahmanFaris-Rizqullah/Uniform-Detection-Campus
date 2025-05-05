import numpy as np
import cv2
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter

class CentroidTracker:
    def __init__(self, max_disappeared=10, iou_threshold=0.3):
        self.next_object_id = 0
        self.objects = {}  # Menyimpan bounding box objek
        self.classes = {}  # Menyimpan class objek
        self.disappeared = {}  # Menyimpan berapa lama objek tidak terdeteksi
        self.kalman_filters = {}  # Menyimpan filter Kalman untuk setiap objek
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold

    def register(self, bbox, cls):
        self.objects[self.next_object_id] = bbox
        self.classes[self.next_object_id] = cls
        self.disappeared[self.next_object_id] = 0
        self.kalman_filters[self.next_object_id] = self.create_kalman_filter(bbox)
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.classes[object_id]
        del self.disappeared[object_id]
        del self.kalman_filters[object_id]

        # Reset ID jika tidak ada objek tersisa
        if len(self.objects) == 0:
            self.next_object_id = 0

    def create_kalman_filter(self, bbox):
        """ Membuat Kalman Filter untuk prediksi posisi objek """
        kf = KalmanFilter(dim_x=4, dim_z=4)
        kf.F = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]])
        kf.H = np.eye(4)
        kf.P *= 1000
        kf.R *= 10
        x1, y1, x2, y2 = bbox
        kf.x = np.array([[x1], [y1], [x2-x1], [y2-y1]])
        return kf

    def compute_iou(self, boxA, boxB):
        """ Menghitung IoU (Intersection over Union) antara dua bounding box """
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        if xB < xA or yB < yA:
            return 0.0

        interArea = (xB - xA) * (yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        return interArea / float(boxAArea + boxBArea - interArea)

    def update(self, rects, classes):
        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
                else:
                    self.kalman_filters[object_id].predict()
                    self.objects[object_id] = self.kalman_filters[object_id].x[:4].flatten()
            return self.objects, self.classes

        if len(self.objects) == 0:
            for i in range(len(rects)):
                self.register(rects[i], classes[i])
        else:
            object_ids = list(self.objects.keys())
            object_bboxes = np.array(list(self.objects.values()))
            input_bboxes = np.array(rects)

            # Buat matriks cost untuk Hungarian Algorithm
            cost_matrix = np.zeros((len(object_bboxes), len(input_bboxes)))

            for i, obj_bbox in enumerate(object_bboxes):
                for j, input_bbox in enumerate(input_bboxes):
                    cost_matrix[i, j] = -self.compute_iou(obj_bbox, input_bbox)  # Minimasi cost

            # Gunakan Hungarian Algorithm untuk mendapatkan pasangan optimal
            object_idxs, input_idxs = linear_sum_assignment(cost_matrix)

            used_rows = set()
            used_cols = set()

            for row, col in zip(object_idxs, input_idxs):
                if cost_matrix[row, col] < -self.iou_threshold:
                    continue

                object_id = object_ids[row]
                self.objects[object_id] = input_bboxes[col]
                self.classes[object_id] = classes[col]
                self.disappeared[object_id] = 0
                self.kalman_filters[object_id].update(np.array([[input_bboxes[col][0]], [input_bboxes[col][1]], [input_bboxes[col][2]], [input_bboxes[col][3]]]))

                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, cost_matrix.shape[0])).difference(used_rows)
            unused_cols = set(range(0, cost_matrix.shape[1])).difference(used_cols)

            if cost_matrix.shape[0] >= cost_matrix.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_bboxes[col], classes[col])

        return self.objects, self.classes
