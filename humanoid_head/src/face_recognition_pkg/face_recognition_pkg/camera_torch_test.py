import torch
import torchvision
import cv2
import numpy as np

# Crete a black image
img = np.zeros((100, 100, 3), dtype=np.uint8)
print("before imshow")
# Show the image
cv2.imshow('Test Window', img)
print("after imshow")
cv2.waitKey(0)
cv2.destroyAllWindows()


# kuweni@ubuntu:~/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg$ python3 face_recognize_active_move.py 
# /home/kuweni/ssd/python_packages/onnxruntime/capi/onnxruntime_inference_collection.py:69: UserWarning: Specified provider 'CUDAExecutionProvider' is not in available provider names.Available providers: 'AzureExecutionProvider, CPUExecutionProvider'
#   warnings.warn(
# SCRFD loaded with providers: ['CPUExecutionProvider']
# SCRFD loaded with providers: ['CPUExecutionProvider']
# [INFO] [1747318083.659584850] [face_recognition_node]: before cam
# cam open
# Node started
# Exception in thread Thread-3:
# Traceback (most recent call last):
#   File "/usr/lib/python3.8/threading.py", line 932, in _bootstrap_inner
#     self.run()
#   File "/usr/lib/python3.8/threading.py", line 870, in run
#     self._target(*self._args, **self._kwargs)
#   File "face_recognize_active_move.py", line 273, in run_recognition
#     self.prev_angle[track_id] = (hor_angle, ver_angle)
# # UnboundLocalError: local variable 'hor_angle' referenced before assignment
# ^C
