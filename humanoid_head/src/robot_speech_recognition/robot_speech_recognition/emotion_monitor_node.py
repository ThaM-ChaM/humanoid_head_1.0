#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import paramiko
import time


class EmotionMonitorNode(Node):
    def __init__(self):
        super().__init__('emotion_monitor_node')
        self.emotion_publisher= self.create_publisher(String, 'detected_emotion', 10)

        # SSH connection info
        self.server_ip = '192.248.10.69'
        self.username = 'fyp3-2'
        self.password = 'cvpr*2022*BSMM'
        self.remote_file_path = '/home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/emotion_classifier/emotions.txt'

        self.get_logger().info("Connecting to server...\n")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.server_ip, username=self.username, password=self.password)

        self.last_line_count = 0

        self.timer = self.create_timer(1.0, self.check_emotion_file)  # Check every second

    def check_emotion_file(self):
        try:
            sftp = self.ssh.open_sftp()
            with sftp.open(self.remote_file_path, 'r') as file:
                lines = file.readlines()
                new_lines = lines[self.last_line_count:]
                self.last_line_count = len(lines)

                for line in new_lines:
                    line = line.strip()
                    if line:
                        emotion = line.split(':')[0].strip()
                        msg = String()
                        msg.data = emotion
                        self.emotion_publisher.publish(msg)
                        self.get_logger().info(f"Published emotion: {emotion}")

            sftp.close()

        except Exception as e:
            self.get_logger().error(f"Error reading from server: {str(e)}")

    def destroy_node(self):
        self.get_logger().info("Shutting down and closing SSH connection...")
        self.ssh.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = EmotionMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
