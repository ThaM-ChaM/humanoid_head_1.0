#!/home/kuweni/ssd/conda/envs/venv/bin/python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import paramiko
import time
import re
from custom_interfaces.msg import People
from custom_interfaces.msg import PeopleArray

class ServerCommunicationNode(Node):
    def __init__(self):
        super().__init__('server_communication_node')
        self.subscription = self.create_subscription(String, 'transcribed_text', self.send_to_server_callback, 10)
        # self.id_server = self.create_publisher(People, "new_user", callback=self.id_server_callback)
        self.new_usr_pub = self.create_publisher(People,"new_user",10)
        self.active_speaker_pub = self.create_publisher(People,"active_speaker",10)
        self.active_usrs_sub = self.create_subscription(PeopleArray,"active_users",self.active_usrs_callback, 10)
        self.user_identity = ''
        
        # Server details
        self.server_ip = '192.248.10.69'
        self.username = 'fyp3-2'
        self.password = 'cvpr*2022*BSMM'
        print("Server Communication Node initialized\n")

    # def id_server_callback(self, request: People.Request, response: People.Response):
    #     self.user_identity = request.id
    #     print(f"incoming identity {self.user_identity}")
    #     if self.user_identity == "Unknown":
    #         response.name = "Isuru"
    #     else:
    #         response.name = self.user_identity
    #     print(f"sending identity {response.name}")
    #     return response

    def extract_name(self, query):
        pattern = r"(?:my name is|i am|it's|call me|you can call me|the name'?s|i'm) (\w+)"
        match = re.search(pattern, query, re.IGNORECASE)
        return match.group(1) if match else "Unknown"

    def send_to_server_callback(self, msg):
        text = msg.data

        sending_text = self.user_identity + " : " + text

        # detected_name = self.extract_name(text)

        # if detected_name != "Unknown":
        #     sending_text = detected_name + " : " + text
        # else:
        #     sending_text = "Isuru : " + text

        self.get_logger().info(f"Received transcribed text: {sending_text}\n")
        
        # start = time.time()

        # # Send text to server
        # ssh = paramiko.SSHClient()
        # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # try:
        #     ssh.connect(self.server_ip, username=self.username, password=self.password)
        #     command = f"echo '{sending_text}' | python3 /home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/user_query_save.py"
        #     stdin, stdout, stderr = ssh.exec_command(command)

        #     response = stdout.read().decode()
        #     errors = stderr.read().decode()

        #     if response:
        #         self.get_logger().info(f"Server Response: {response}\n")
        #     if errors:
        #         self.get_logger().error(f"Errors: {errors}\n")

        #     end = time.time()

        #     self.get_logger().info(f"Time taken to send the query to the server: {end - start:.5f}s")

        # finally:
        #     ssh.close()

    def active_usrs_callback(self, msg:PeopleArray):
        pass

def main(args=None):
    rclpy.init(args=args)
    server_communication_node = ServerCommunicationNode()
    rclpy.spin(server_communication_node)
    server_communication_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()