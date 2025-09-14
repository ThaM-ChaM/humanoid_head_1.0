import os
import csv
import time
import cv2
from datetime import datetime

SAVE_DIR = "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/Testing/CSV"
os.makedirs(SAVE_DIR, exist_ok=True)

CSV_PATH = os.path.join(SAVE_DIR, "unknown_enrollment_log.csv")

# Initialize CSV with headers if not exists
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Image Path", "Label", "Was Unknown", "Unknown ID", "Enrollment Time", "Label Change Time"])


def generate_unique_filename(track_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"face_{track_id}_{timestamp}.jpg"


def log_unknown_and_enrollment(
    face_img,
    label,
    was_unknown=True,
    unknown_id=None,
    enrollment_time=None,
    label_change_time=None
):
    if face_img is None or unknown_id is None:
        return

    filename = generate_unique_filename(unknown_id)
    image_path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(image_path, face_img)

    row = [
        image_path,
        label,
        "Yes" if was_unknown else "No",
        unknown_id,
        round(enrollment_time, 3) if enrollment_time else "",
        round(label_change_time, 3) if label_change_time else ""
    ]

    with open(CSV_PATH, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
