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

# from sensor_msgs.msg import Image
from cv_bridge import CvBridge


from custom_interfaces.srv import GivePeopleName
from custom_interfaces.msg import People
from custom_interfaces.msg import PeopleArray
# from functools import partial

from face_recognition_pkg.face_alignment.alignment import norm_crop
from face_recognition_pkg.face_detection.scrfd.detector import SCRFD
from face_recognition_pkg.face_recognition.arcface.model import iresnet_inference
from face_recognition_pkg.face_recognition.arcface.utils import compare_encodings, read_features
from face_recognition_pkg.face_tracking.tracker.byte_tracker import BYTETracker
from face_recognition_pkg.face_tracking.tracker.visualize import plot_tracking
import face_recognition_pkg.add_persons as add_persons

# from face_alignment.alignment import norm_crop
# from face_detection.scrfd.detector import SCRFD
# from face_recognition.arcface.model import iresnet_inference
# from face_recognition.arcface.utils import compare_encodings, read_features
# from face_tracking.tracker.byte_tracker import BYTETracker
# from face_tracking.tracker.visualize import plot_tracking
# import add_persons # as add_persons

class FaceRecognitionNode(Node):
    def __init__(self):
        super().__init__('face_recognition_node')

        self.bridge = CvBridge()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.detector = SCRFD(model_file="/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_detection/scrfd/weights/scrfd_2.5g_bnkps.onnx")
        self.recognizer = iresnet_inference(
            model_name="r100",
            path="/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_recognition/arcface/weights/arcface_r100.pth",
            device=self.device
        )
        self.latest_frame = None
        self.images_names, self.images_embs = read_features(feature_path="/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/datasets/face_features/feature")
        self.id_face_mapping = {}
        self.unknown = []
        self.active_usrs = PeopleArray()
        self.active_usrs.data = []
        self.new_person_base = "/home/kuweni/ssd/Charu/face_recog_testing/face-recognition/datasets/new_persons"

        self.id_server = self.create_service(GivePeopleName, "user_id", callback=self.id_server_callback)
        self.new_usr_sub = self.create_subscription(People,"new_user",self.new_usr_callback,10)
        self.active_usr_pub = self.create_publisher(PeopleArray,"active_users",10)

        config_path = "/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/face_tracking/config/config_tracking.yaml"
        self.config_tracking = self.load_config(config_path)

        self.tracker = BYTETracker(args=self.config_tracking, frame_rate=30)
        self.frame_id = 0
        self.data_mapping = {}
        self.get_logger().info("before cam")

        self.cap = cv2.VideoCapture('/dev/UVCwebcam', cv2.CAP_V4L2)
        self.prev_recognition_bbox = {}  # track_id → [x1, y1, x2, y2]
        self.recognition_iou_thresh = 0.8  # similarity threshold (higher = stricter)
        self.prev_angle = {}  # track_id → (hor_angle, ver_angle)
        self.angle_change_thresh = 10  # degrees


        # self.cap = cv2.VideoCapture('/dev/video2')

        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.display_thread = threading.Thread(target=self.display_loop)
        self.display_thread.start()



        if self.cap.isOpened():
            print("cam open")
        else:
            print("cam not open")


        self.tracking_thread = threading.Thread(target=self.run_tracking)
        self.recognition_thread = threading.Thread(target=self.run_recognition)
        print("Node started")

        self.tracking_thread.start()
        self.recognition_thread.start()

    def display_loop(self):
        time.sleep(1)
        while rclpy.ok():
            if self.latest_frame is not None:
                cv2.imshow("Face Recognition 1", self.latest_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    rclpy.shutdown()
                    break

        cv2.destroyAllWindows()

    def load_config(self, file_name):
        with open(file_name, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.get_logger().error(str(exc))
                return {}


    @torch.no_grad()
    def get_feature(self, face_image):

    # Get features of one face image

        face_preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Resize((112, 112)),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])
        
        face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        face_image = face_preprocess(face_image).unsqueeze(0).to(self.device)
        emb = self.recognizer(face_image).cpu().numpy()
        return emb / np.linalg.norm(emb)


    def run_tracking(self):
        fps = -1
        frame_count = 0
        start_time = time.time_ns()

        while rclpy.ok():
            if not self.cap.grab():  # skip decode to keep buffer fresh
                continue

            ret, frame = self.cap.retrieve()
            if not ret:
                # print("no ret")
                continue          # self.get_logger().info(f"no of unknown {len(self.unknown)}")

                        # updated = False
                        # for usr in self.active_usrs:
                        #     if usr["id"] == tracking_ids[i]:
                        #         usr["angle"] = hor_angle
                        #         usr["name"] = caption.split(":")[0]
                        #         usr["missed_frames"] = 0
                        #         updated = True
                        #         break
                        # if not updated:
                        #     self.active_usrs.append({
                        #         "id": tracking_ids[i],
                        #         "name": caption.split(":")[0],
                        #         "angle": hor_angle,
                        #         "missed_frames": 0,
                        #         "image": aligned_face
                        #     })

            try:
                tracking_image, data = self.process_tracking(frame, fps)
                self.latest_frame = tracking_image.copy()
                self.data_mapping = data
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
            outputs, img_info, bboxes, landmarks = self.detector.detect_tracking(image=frame, thresh=0.45)
        except Exception as e:
            self.get_logger().warn(f"Detection failed: {e}")
            return frame, {}

        tracking_bboxes, tracking_ids = [], []

        if outputs is not None:
            online_targets = self.tracker.update(outputs, [img_info["height"], img_info["width"]], (128, 128))

            for t in online_targets:
                tlwh = t.tlwh
                if tlwh[2] * tlwh[3] > self.config_tracking["min_box_area"]:
                    x1, y1, w, h = tlwh
                    tracking_bboxes.append([x1, y1, x1 + w, y1 + h])
                    tracking_ids.append(t.track_id)

            tracking_image = plot_tracking(img_info["raw_img"], [t.tlwh for t in online_targets], tracking_ids, names=self.id_face_mapping, frame_id=self.frame_id, fps=fps)
        else:
            tracking_image = frame.copy()  # fallback if detection failed silently

        self.frame_id += 1

        data = {
            "raw_image": frame,
            "detection_bboxes": bboxes if outputs is not None else [],
            "detection_landmarks": landmarks if outputs is not None else [],
            "tracking_ids": tracking_ids,
            "tracking_bboxes": tracking_bboxes,
        }

        if fps > 0:
            cv2.putText(
                tracking_image,
                f"Active: {len(self.id_face_mapping)}",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2,
                cv2.LINE_AA
            )
        return tracking_image, data



    def run_recognition(self):
        while rclpy.ok():
            data = self.data_mapping
            if not data:
                continue

            raw_image = data.get("raw_image")
            detection_bboxes = data.get("detection_bboxes", [])
            detection_landmarks = data.get("detection_landmarks", [])
            tracking_bboxes = data.get("tracking_bboxes", [])
            tracking_ids = data.get("tracking_ids", [])

            for i, track_bbox in enumerate(tracking_bboxes):
                track_id = tracking_ids[i]

                # Skip if IoU with previous bbox is too high (i.e., not much change)
                prev_bbox = self.prev_recognition_bbox.get(track_id)
                bbox_skip = False

                # Always compute angles before potential usage
                x_min, y_min, x_max, y_max = track_bbox
                bbox_center_x = (x_min + x_max) / 2
                frame_width = raw_image.shape[1]
                hor_angle = max(-60, min(60, round(((bbox_center_x / frame_width) - 0.5) * -120, 2)))

                bbox_center_y = (y_min + y_max) / 2
                frame_height = raw_image.shape[0]
                ver_angle = max(-30, min(30, round(((bbox_center_y / frame_height) - 0.5) * -60, 2)))

                if prev_bbox is not None and self.compute_iou(track_bbox, prev_bbox) > self.recognition_iou_thresh:
                    prev_hor, prev_ver = self.prev_angle.get(track_id, (None, None))
                    if prev_hor is not None and abs(hor_angle - prev_hor) < self.angle_change_thresh and abs(ver_angle - prev_ver) < self.angle_change_thresh:
                        bbox_skip = True


                if bbox_skip:
                    # self.get_logger().info(f"Skipped ArcFace for ID {track_id} due to stable bbox and angle.")
                    continue

                for j, det_bbox in enumerate(detection_bboxes):
                    if self.mapping_bbox(track_bbox, det_bbox) > 0.9:
                        # Save the current state for next comparison
                        self.prev_recognition_bbox[track_id] = track_bbox
                        self.prev_angle[track_id] = (hor_angle, ver_angle)
                        self.get_logger().info(f"Running ArcFace for ID {track_id}")

                        aligned_face = norm_crop(img=raw_image, landmark=detection_landmarks[j])
                        score, name = self.recognize_face(aligned_face)

                        caption = "Unknown" if name is not None and score < 0.4 else f"{name}:{score:.2f}"
                        if caption == "Unknown":
                            self.get_logger().info("Unknown person")

                        self.id_face_mapping[track_id] = caption

                        x_min, y_min, x_max, y_max = track_bbox
                        bbox_center_x = (x_min + x_max) / 2
                        frame_width = raw_image.shape[1]
                        relative_x = (bbox_center_x / frame_width) - 0.5
                        hor_angle = max(-60, min(60, round(relative_x * -120, 2)))

                        bbox_center_y = (y_min + y_max) / 2
                        frame_height = raw_image.shape[0]
                        relative_y = (bbox_center_y / frame_height) - 0.5
                        ver_angle = max(-30, min(30, round(relative_y * -60, 2)))

                        self.get_logger().info(f"{caption} hor_angle {hor_angle}, ver_angle {ver_angle}")

                        for usr in self.active_usrs.data:
                            if usr.id == track_id:
                                usr.hor_angle = int(hor_angle)
                                usr.ver_angle = int(ver_angle)
                                usr.name = caption.split(":")[0]
                                usr.missed_frames = 0
                                break
                        else:
                            new_usr = People()
                            new_usr.id = track_id
                            new_usr.name = caption.split(":")[0]
                            new_usr.hor_angle = int(hor_angle)
                            new_usr.ver_angle = int(ver_angle)
                            new_usr.missed_frames = 0
                            self.active_usrs.data.append(new_usr)

                            self.unknown.append({
                                "id": track_id,
                                "angle": hor_angle,
                                "image": aligned_face
                            })
                        break  # once matched

            # Clean up old IDs
            current_ids = set(tracking_ids)
            for usr in self.active_usrs.data:
                if usr.id in current_ids:
                    usr.missed_frames = 0
                else:
                    usr.missed_frames += 1

            remove_ids = [p.id for p in self.active_usrs.data if p.missed_frames > 50]
            self.active_usrs.data = [p for p in self.active_usrs.data if p.id not in remove_ids]
            self.unknown = [u for u in self.unknown if u["id"] not in remove_ids]
            self.active_usr_pub.publish(self.active_usrs)

            # Clean up unused bbox cache
            for old_id in list(self.prev_recognition_bbox):
                if old_id not in current_ids:
                    del self.prev_recognition_bbox[old_id]
            for old_id in list(self.prev_angle):
                if old_id not in current_ids:
                    del self.prev_angle[old_id]


    def compute_iou(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        inter_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - inter_area

        return inter_area / union_area if union_area > 0 else 0


    def add_new_person(self,image,name):
        add_persons.add_person(image,name)
        self.images_names, self.images_embs = read_features("/home/kuweni/ssd/ros2_ws/src/face_recognition_pkg/face_recognition_pkg/datasets/face_features/feature")


    def id_server_callback(self, request: GivePeopleName.Request,response:GivePeopleName.Response):
        self.get_logger().info("id_server request received")
        doa = request.doa
        # print(f"requested DOA {doa}")
        min_dif = 5
        for usr in self.active_usrs.data:
            if abs(usr["angle"] - doa) < min_dif:
                response.name = usr["name"]
                min_dif = abs(usr["angle"] - doa)
        if response.name == "":
            response.name = "no matching user"
        self.get_logger().info("id_server response sent")
        return response


    def new_usr_callback(self,msg:People):
        
        id = msg.id
        name = msg.name
        self.get_logger().warn(f"got name {name}, id {id}")
        for usr in self.active_usrs.data:
            if usr.id == id:
                usr.name = name
                break
            
        for usr in self.unknown:
            if usr["id"] == id:
                img = usr["image"]
                self.add_new_person(img,name)
                self.get_logger().warn(f"added person {name}")
                self.unknown.remove(usr)
                break
        

    def recognize_face(self, face_image):
        query_emb = self.get_feature(face_image)
        score, id_min = compare_encodings(query_emb, self.images_embs)
        return score[0], self.images_names[id_min]

 
    def mapping_bbox(self, box1, box2):
        x_min_inter = max(box1[0], box2[0])
        y_min_inter = max(box1[1], box2[1])
        x_max_inter = min(box1[2], box2[2])
        y_max_inter = min(box1[3], box2[3])
        inter_area = max(0, x_max_inter - x_min_inter + 1) * max(0, y_max_inter - y_min_inter + 1)
        area1 = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
        area2 = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
        return inter_area / float(area1 + area2 - inter_area)


def main(args=None):
    rclpy.init(args=args)
    node = FaceRecognitionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Shutting down...")

    node.destroy_node()
    rclpy.shutdown()






if __name__ == "__main__":
    main()