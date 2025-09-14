#!/home/kuweni/ssd/conda/envs/face_rec/bin/python3
import rclpy
from rclpy.node import Node
from torchvision import transforms
import cv2
import time
import numpy as np
import threading
import torch
import yaml

from cv_bridge import CvBridge
from custom_interfaces.msg import People, PeopleArray
from face_recognition_pkg.face_detection.scrfd.detector import SCRFD
from face_recognition_pkg.face_tracking.tracker.byte_tracker import BYTETracker
from face_recognition_pkg.face_tracking.tracker.visualize import plot_tracking

class FaceTrackingOnlyNode(Node):
    def __init__(self):
        super().__init__('face_tracking_only_node')

        self.bridge = CvBridge()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.detector = SCRFD(model_file="/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
        config_path = "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_tracking/config/config_tracking.yaml"
        self.config_tracking = self.load_config(config_path)

        self.tracker = BYTETracker(args=self.config_tracking, frame_rate=30)
        self.frame_id = 0

        self.cap = cv2.VideoCapture('/dev/UVCwebcam', cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if self.cap.isOpened():
            print("cam open")
        else:
            print("cam not open")

        self.display_thread = threading.Thread(target=self.display_loop)
        self.display_thread.start()

        self.tracking_thread = threading.Thread(target=self.run_tracking)
        self.tracking_thread.start()

    def load_config(self, file_name):
        with open(file_name, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.get_logger().error(str(exc))
                return {}

    def display_loop(self):
        time.sleep(1)
        while rclpy.ok():
            if hasattr(self, 'latest_frame') and self.latest_frame is not None:
                disp_frame = cv2.resize(self.latest_frame, (640, 360))
                cv2.imshow("Face Tracking Only", disp_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    rclpy.shutdown()
                    break
        cv2.destroyAllWindows()

    def run_tracking(self):
        fps = -1
        frame_count = 0
        start_time = time.time_ns()

        while rclpy.ok():
            for _ in range(2):
                self.cap.grab()
            ret, frame = self.cap.retrieve()

            if not ret:
                print("no ret")
                continue

            try:
                tracking_image = self.process_tracking(frame, fps)
                self.latest_frame = tracking_image.copy()
            except Exception as e:
                self.get_logger().warn(f"Tracking pipeline failed: {e}")
                continue

            frame_count += 1
            if frame_count >= 10:
                fps = 1e9 * frame_count / (time.time_ns() - start_time)
                frame_count = 0
                start_time = time.time_ns()

    def process_tracking(self, frame, fps):
        try:
            outputs, img_info, _, _ = self.detector.detect_tracking(image=frame, thresh=0.45)
        except Exception as e:
            self.get_logger().warn(f"Detection failed: {e}")
            return frame

        tracking_image = frame.copy()
        if outputs is not None:
            online_targets = self.tracker.update(outputs, [img_info["height"], img_info["width"]], (128, 128))
            tlwhs = [t.tlwh for t in online_targets]
            ids = [t.track_id for t in online_targets]
            tracking_image = plot_tracking(img_info["raw_img"], tlwhs, ids, frame_id=self.frame_id, fps=fps)

        self.frame_id += 1
        return tracking_image

def main(args=None):
    rclpy.init(args=args)
    node = FaceTrackingOnlyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Shutting down...")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
