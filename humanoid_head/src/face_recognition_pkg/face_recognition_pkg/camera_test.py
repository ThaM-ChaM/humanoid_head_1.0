import cv2
import torch
import torchvision
import numpy as np

print("Torch:", torch.__version__)
print("Torchvision:", torchvision.__version__)
print("OpenCV:", cv2.__version__)

cap = cv2.VideoCapture('/dev/UVCwebcam')
if not cap.isOpened():
    print("Camera not found")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Optional torchvision transform
    # tensor = torchvision.transforms.ToTensor()(frame)

    cv2.imshow("Jetson Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# (face_rec) kuweni@ubuntu:~/ssd$ /home/kuweni/ssd/conda/envs/face_rec/bin/python /home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognize_active.py
# [INFO] [1747032081.640967519] [face_recognition_node]: before cam
# [ WARN:0] global /home/ubuntu/build_opencv/opencv/modules/videoio/src/cap_gstreamer.cpp (2075) handleMessage OpenCV | GStreamer warning: Embedded video playback halted; module source reported: Could not read from resource.
# [ WARN:0] global /home/ubuntu/build_opencv/opencv/modules/videoio/src/cap_gstreamer.cpp (1053) open OpenCV | GStreamer warning: unable to start pipeline
# [ WARN:0] global /home/ubuntu/build_opencv/opencv/modules/videoio/src/cap_gstreamer.cpp (616) isPipelinePlaying OpenCV | GStreamer warning: GStreamer: pipeline have not been created
# cam open
# Node started

# (face_rec) kuweni@ubuntu:~/ssd$ /home/kuweni/ssd/conda/envs/face_rec/bin/python /home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognize_active.py
# [INFO] [1747033328.289075067] [face_recognition_node]: before cam
# cam open
# Node started
# Exception in thread Thread-2:
# Traceback (most recent call last):
#   File "/home/kuweni/ssd/conda/envs/face_rec/lib/python3.8/threading.py", line 932, in _bootstrap_inner
#     self.run()
#   File "/home/kuweni/ssd/conda/envs/face_rec/lib/python3.8/threading.py", line 870, in run
#     self._target(*self._args, **self._kwargs)
#   File "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognize_active.py", line 142, in run_tracking
#     self.latest_frame = np.hstack((frame, tracking_image))
# UnboundLocalError: local variable 'tracking_image' referenced before assignment

# kuweni@ubuntu:~/ssd$ /usr/bin/python3 /home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognize_testing.py
# Traceback (most recent call last):
#   File "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognize_testing.py", line 25, in <module>
#     from face_recognition_pkg.face_tracking.tracker.byte_tracker import IoUTracker
# ImportError: cannot import name 'IoUTracker' from 'face_recognition_pkg.face_tracking.tracker.byte_tracker' (/home/kuweni/ssd/ros2_ws/install/face_recognition_pkg/lib/python3.8/site-packages/face_recognition_pkg/face_tracking/tracker/byte_tracker.py)







# kuweni@ubuntu:~/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg$ python3 face_recognize_test.py 
# /home/kuweni/ssd/python_packages/onnxruntime/capi/onnxruntime_inference_collection.py:69: UserWarning: Specified provider 'TensorrtExecutionProvider' is not in available provider names.Available providers: 'AzureExecutionProvider, CPUExecutionProvider'
#   warnings.warn(
# /home/kuweni/ssd/python_packages/onnxruntime/capi/onnxruntime_inference_collection.py:69: UserWarning: Specified provider 'CUDAExecutionProvider' is not in available provider names.Available providers: 'AzureExecutionProvider, CPUExecutionProvider'
#   warnings.warn(
# Traceback (most recent call last):
#   File "face_recognize_test.py", line 36, in <module>
#     import add_persons # as add_persons
#   File "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/add_persons.py", line 21, in <module>
#     detector = SCRFD(model_file="/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_detection/scrfd/weights/scrfd_fp16.engine")
#   File "/home/kuweni/ssd/ros2_ws/install/face_recognition_pkg/lib/python3.8/site-packages/face_recognition_pkg/face_detection/scrfd/detector.py", line 76, in __init__
#     self.session = onnxruntime.InferenceSession(
#   File "/home/kuweni/ssd/python_packages/onnxruntime/capi/onnxruntime_inference_collection.py", line 419, in __init__
#     self._create_inference_session(providers, provider_options, disabled_optimizers)
#   File "/home/kuweni/ssd/python_packages/onnxruntime/capi/onnxruntime_inference_collection.py", line 452, in _create_inference_session
#     sess = C.InferenceSession(session_options, self._model_path, True, self._read_config_from_model)
# onnxruntime.capi.onnxruntime_pybind11_state.NoSuchFile: [ONNXRuntimeError] : 3 : NO_SUCHFILE : Load model from scrfd_fp16.engine failed:Load model scrfd_fp16.engine failed. File doesn't exist