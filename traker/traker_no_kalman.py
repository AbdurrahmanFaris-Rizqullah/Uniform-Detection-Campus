import numpy as np

class CentroidTracker:
    def __init__(self, max_disappeared=10):
        self.next_object_id = 0
        self.objects = {}  # object_id: {"centroid": (x, y), "class_name": str, "bbox": (x1, y1, x2, y2)}
        self.disappeared = {}
        self.max_disappeared = max_disappeared

    def register(self, centroid, class_name="object", bbox=None):
        self.objects[self.next_object_id] = {
            "centroid": centroid,
            "class_name": class_name,
            "bbox": bbox
        }
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, rects, class_names=None):
        if class_names is None:
            class_names = ["object"] * len(rects)

        if len(rects) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = np.zeros((len(rects), 2), dtype="int")

        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            input_centroids[i] = (cX, cY)

        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i], class_names[i], rects[i])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = [self.objects[object_id]["centroid"] for object_id in object_ids]
            object_centroids = np.array(object_centroids)

            D = np.linalg.norm(object_centroids[:, np.newaxis] - input_centroids, axis=2)

            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                object_id = object_ids[row]
                self.objects[object_id]["centroid"] = input_centroids[col]
                self.objects[object_id]["bbox"] = rects[col]
                self.disappeared[object_id] = 0
                used_rows.add(row)
                used_cols.add(col)

            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)

            if D.shape[0] >= D.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                for col in unused_cols:
                    self.register(input_centroids[col], class_names[col], rects[col])

        return self.objects
