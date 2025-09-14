import subprocess
import time
from datetime import datetime

LOG_FILE = "/home/kuweni/ssd/ros2_ws/jetson_monitor.log"  # Change this path if needed

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_dmesg_tail():
    try:
        output = subprocess.check_output(["dmesg", "-T"], stderr=subprocess.STDOUT)
        return output.decode("utf-8").strip()
    except Exception as e:
        return f"dmesg error: {e}"

def get_tegrastats():
    try:
        # output = subprocess.check_output(["tegrastats"], stderr=subprocess.STDOUT, timeout=5)
        output = subprocess.check_output(["timeout", "1s", "tegrastats"], stderr=subprocess.STDOUT)
        return output.decode("utf-8").strip()
    except Exception as e:
        return f"tegrastats error: {e}"

def main():
    log("===== Logging started =====")
    while True:
        try:
            dmesg_logs = get_dmesg_tail()
            tegra_logs = get_tegrastats()

            log("---- dmesg ----")
            log(dmesg_logs)
            log("---- tegrastats ----")
            log(tegra_logs)
            time.sleep(60)  # log every 60 seconds (you can change this)
        except KeyboardInterrupt:
            log("===== Logging stopped by user =====")
            break
        except Exception as e:
            log(f"Unhandled error: {e}")

if __name__ == "__main__":
    main()
