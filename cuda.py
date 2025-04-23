import cv2
print('CUDA support:', 'Yes' if cv2.cuda.getCudaEnabledDeviceCount() > 0 else 'No')