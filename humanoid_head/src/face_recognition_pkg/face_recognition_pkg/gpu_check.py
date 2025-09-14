import torch


import cv2
# import torchvision


if torch.cuda.is_available():
    print("CUDA is available! GPU is ready to use.")
    print("GPU Name:", torch.cuda.get_device_name(0))
else:
    print("CUDA is NOT available. Using CPU.")

# Try opening camera 0
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    cv2.imshow('Camera Feed', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
