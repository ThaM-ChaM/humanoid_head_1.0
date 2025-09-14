import cv2
import os
import csv
import uuid

def log_recognition_result(face_image, recognized_name):
    os.makedirs("face_recognition_tests/accuracy_faces", exist_ok=True)
    face_id = str(uuid.uuid4())
    image_path = f"face_recognition_tests/accuracy_faces/{face_id}.jpg"
    cv2.imwrite(image_path, face_image)

    with open("face_recognition_tests/recognition_accuracy.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([image_path, recognized_name])