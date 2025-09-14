import time
import csv

fps_log_file = "face_recognition_tests/fps_log.csv"
frame_times = []
frame_counts = []
last_logged_time = time.time()

def log_fps(frame_id, active_people):
    global frame_times, frame_counts, last_logged_time

    now = time.time()
    frame_times.append(now)
    frame_counts.append((frame_id, active_people))

    if len(frame_times) >= 10:
        elapsed = frame_times[-1] - frame_times[0]
        fps = len(frame_times) / elapsed if elapsed > 0 else 0
        with open(fps_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), frame_counts[-1][0], active_people, round(fps, 2)])
        frame_times = []
        frame_counts = []