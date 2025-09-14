#!/home/kuweni/ssd/conda/envs/tharusha/bin/python3

import rclpy
from rclpy.node import Node
import cv2
import torch
from ultralytics import YOLO
from geometry_msgs.msg import Point

class FaceTrackerNode(Node):
    def __init__(self, fps):
        super().__init__("face_tracker")

        # ROS2 Publisher
        self.publisher_ = self.create_publisher(Point, "face_track", 10)

        # Load YOLOv8 model and move to GPU
        model_path = 'yolov8n.pt'
        self.model = YOLO(model_path).to("cuda")

        # Load NVIDIA's optimized face detection model
        self.face_model = cv2.dnn.readNetFromCaffe(
            "/home/kuweni/models/face_detection/deploy.prototxt",
            "/home/kuweni/models/face_detection/res10_300x300_ssd_iter_140000_fp16.caffemodel"
        )

        self.face_model.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.face_model.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

        # Open webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.get_logger().info("Error: Could not open the webcam.")
            exit()

        # Set processing timer
        self.create_timer(1.0 / fps, self.process_frame)
        self.get_logger().info("Face tracker has started.")

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error("Failed to grab frame")
            return

        # Upload frame to GPU
        frame_gpu = cv2.cuda_GpuMat()
        frame_gpu.upload(frame)
        frame = frame_gpu.download()  # Download back after processing

        # YOLOv8 person detection
        results = self.model(frame, device="cuda")

        for result in results[0].boxes:
            box = result.xyxy[0].cpu().numpy()
            conf = result.conf.item()
            class_id = int(result.cls.item())

            if class_id == 0 and conf > 0.5:  # Class 0 = person
                x1, y1, x2, y2 = map(int, box)

                # Extract upper body for face detection
                person_roi = frame[y1:y2, x1:x2]

                # Prepare image for face detection
                blob = cv2.dnn.blobFromImage(person_roi, scalefactor=1.0, size=(300, 300),
                                             mean=(104.0, 177.0, 123.0), swapRB=False, crop=False)
                self.face_model.setInput(blob)
                faces = self.face_model.forward()

                for i in range(faces.shape[2]):
                    confidence = faces[0, 0, i, 2]
                    if confidence > 0.5:
                        fx, fy, fw, fh = faces[0, 0, i, 3:7] * [x2 - x1, y2 - y1, x2 - x1, y2 - y1]
                        fx, fy, fw, fh = int(fx), int(fy), int(fw), int(fh)

                        # Draw face bounding box
                        cv2.rectangle(frame, (x1 + fx, y1 + fy), (x1 + fx + fw, y1 + fy + fh), (255, 0, 0), 2)

                        # Calculate center
                        center_x = x1 + fx + fw // 2
                        center_y = y1 + fy + fh // 2
                        cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

                        # Publish face center coordinates
                        msg = Point()
                        msg.x = float(center_x)
                        msg.y = float(center_y)
                        msg.z = 0.0
                        self.publisher_.publish(msg)
                        break
                break

        # Display frame
        cv2.imshow('Jetson YOLOv8 Face Tracking', frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.cap.release()
            cv2.destroyAllWindows()
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = FaceTrackerNode(30)
    rclpy.spin(node)
    node.cap.release()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
