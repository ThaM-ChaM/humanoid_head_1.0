import time
import csv

latency_log_file = "face_recognition_tests/recognition_latency.csv"

def log_start_time(frame_id):
    return (frame_id, time.time())

def log_end_time(frame_id, start_time):
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000
    with open(latency_log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([frame_id, start_time, end_time, latency_ms])