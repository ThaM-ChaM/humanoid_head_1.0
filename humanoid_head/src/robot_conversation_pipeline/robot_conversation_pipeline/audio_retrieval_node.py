# # !/home/dell/miniconda3/envs/stt_env/bin/python3

# # import os
# # import time
# # import rclpy
# # import paramiko
# # from rclpy.node import Node
# # from std_msgs.msg import String
# # from playsound import playsound

# # class AudioPlayer(Node):
# #     """ROS2 Node for handling and playing audio responses from the server."""

# #     def __init__(self):
# #         super().__init__('audio_player')

# #         # ROS2 Subscription for receiving audio file paths
# #         self.subscription = self.create_subscription(String,'response_audio_path',self.response_audio_path_callback,10)
# #         self.publisher = self.create_publisher(String,'robot_responding_flag',10)
# #         # Configuration for SSH connection
# #         # Server details
# #         self.server_ip = "192.248.10.69"
# #         self.username = "fyp3-2"
# #         self.password = "cvpr*2022*BSMM"
# #         self.remote_audio_dir = "/home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/audio_output_response_records"
# #         self.local_audio_dir = "/media/kuweni/SSD/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios"


# #         # Track downloaded files to avoid duplicates
# #         self.downloaded_files = set()

# #         # State management variables
# #         self.is_playing = False
# #         self.last_publish_time = None

# #         self.get_logger().info("AudioPlayer node initialized successfully.")

# #     def response_audio_path_callback(self, msg):
# #         """Handles the response audio file path received from the topic."""
# #         response_audio_path = msg.data.strip()

# #         if not response_audio_path:
# #             self.get_logger().warn("Received an empty audio file path.")
# #             return

# #         self.last_publish_time = time.time()
# #         self.get_logger().info(f"Received response audio file path: {response_audio_path}")

# #         if os.path.exists(response_audio_path):
# #             self.play_audio(response_audio_path)
# #         else:
# #             self.get_logger().warn(f"Audio file not found: {response_audio_path}")

# #     def play_audio(self, file_path):
# #         """Plays the specified audio file if it's not already playing."""
# #         if self.is_playing:
# #             self.get_logger().warn("Audio is already playing. Skipping new playback.")
# #             return

# #         if os.path.exists(file_path):
# #             self.is_playing = True
# #             self.get_logger().info(f"Playing audio from: {file_path}")
            
# #             # Publish a message to indicate that the robot is responding
# #             robot_responding_msg = String()
# #             robot_responding_msg.data = "True"
# #             self.publisher.publish(robot_responding_msg)
        
# #             playsound(file_path)

# #             self.is_playing = False
# #             self.get_logger().info("Audio playback completed.")
            
# #             # Publish a message to indicate that the robot has finished responding
# #             robot_responding_msg.data = "False"
# #             self.publisher.publish(robot_responding_msg)
            
# #             # Calculate total response time if available
# #             if self.last_publish_time:
# #                 total_delay = time.time() - self.last_publish_time
# #                 self.get_logger().info(f"Total time taken to respond: {total_delay:.3f}s")
# #         else:
# #             self.get_logger().warn(f"Audio file not found at {file_path}.")

# #     def retrieve_audio(self):
# #         """Retrieves and plays new audio files from the remote server via SSH."""
# #         ssh = paramiko.SSHClient()
# #         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# #         try:
# #             ssh.connect(self.server_ip, username=self.username, password=self.password)
# #             sftp = ssh.open_sftp()

# #             # List all available .wav files
# #             command = f"ls {self.remote_audio_dir}/*.wav 2>/dev/null"
# #             stdin, stdout, stderr = ssh.exec_command(command)
# #             files = stdout.read().decode().strip().split("\n")
# #             errors = stderr.read().decode().strip()

# #             if errors:
# #                 self.get_logger().warn(f"Error retrieving files: {errors}")
# #                 return

# #             for file_path in files:
# #                 if file_path and file_path not in self.downloaded_files:
# #                     file_name = os.path.basename(file_path)
# #                     local_path = os.path.join(self.local_audio_dir, file_name)

# #                     # Download the file
# #                     self.get_logger().info(f"New file detected: {file_name}. Downloading...")
# #                     sftp.get(file_path, local_path)
# #                     self.get_logger().info(f"Downloaded: {file_name}")

# #                     self.downloaded_files.add(file_path)
# #                     self.play_audio(local_path)

# #             sftp.close()

# #         except Exception as e:
# #             self.get_logger().error(f"Error retrieving audio files: {e}")
# #         finally:
# #             ssh.close()

# #     def run(self):
# #         """Continuously monitors the server for new audio files."""
# #         self.get_logger().info("Starting continuous audio monitoring...")
# #         while rclpy.ok():
# #             self.retrieve_audio()
# #             time.sleep(1)  # Adjusted for efficiency

# # def main(args=None):
# #     """Main function to run the AudioPlayer node."""
# #     rclpy.init(args=args)
# #     audio_player = AudioPlayer()

# #     try:
# #         audio_player.run()
# #     except KeyboardInterrupt:
# #         audio_player.get_logger().info("Shutting down AudioPlayer node.")
# #     finally:
# #         audio_player.destroy_node()
# #         rclpy.shutdown()

# # if __name__ == '__main__':
# #     main()



# import rclpy
# from rclpy.node import Node
# import paramiko
# import os
# import time
# from playsound import playsound
# from std_msgs.msg import Bool, String, Int32, Empty
# import contextlib
# import sys


# class AudioRetrievalNode(Node):
#     def __init__(self):
#         super().__init__('audio_retrieval_node')
        
#         # Server details
#         self.server_ip = "192.248.10.69"
#         self.username = "fyp3-2"
#         self.password = "cvpr*2022*BSMM"
#         self.remote_audio_dir = "/home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/audio_output_response_records"
#         self.local_audio_dir = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios"
#         self.downloaded_files = set()
        
#         # Ensure the local directory exists
#         if not os.path.exists(self.local_audio_dir):
#             os.makedirs(self.local_audio_dir)

#         # Timer to check for new audio files periodically
#         self.timer = self.create_timer(0.5, self.retrieve_audio)  # Check every 500 ms second
#         self.get_logger().info("Audio Retrieval Node has started.")

#         self.publisher_mouth_flag = self.create_publisher(Bool, 'mouth_flag', 10)
#         self.publisher_audio_path = self.create_publisher(String, 'audio_response_path', 10)
#         self.publisher_end_audio_response = self.create_publisher(Bool, 'end_audio_response', 10)

#         self.subscriptions_unclear_audio = self.create_subscription(String, 'unclear_audio_path', self.unclear_audio_path_callback, 10)
#         self.subscription_time = self.create_subscription(Int32, 'full_process_time', self.full_processing_time_callback, 10)
#         self.human_speech_detected_time = 0
#         self.node_start_time = time.time()


#     def full_processing_time_callback(self, msg):
#         self.human_speech_start_time = msg.data


#     def unclear_audio_path_callback(self, msg):
#         unclear_audio_path = msg.data
#         self.play_audio(unclear_audio_path)


#     def retrieve_audio(self):
#         # self.get_logger().info("Checking server for new audio files...")
#         # msg_end_reponse = Bool()
#         # msg_end_reponse.data = False
#         # self.publisher_end_audio_response.publish(msg_end_reponse)
#         # self.get_logger().info(f"End audio reponse is, {msg_end_reponse}")

        
#         ssh = paramiko.SSHClient()
#         ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#         try:
#             ssh.connect(self.server_ip, username=self.username, password=self.password)
            
#             command = f"ls {self.remote_audio_dir}/*.wav 2>/dev/null"
#             stdin, stdout, stderr = ssh.exec_command(command)
#             files = stdout.read().decode().strip().split("\n")
#             errors = stderr.read().decode().strip()

#             if errors:
#                 self.get_logger().error(f"Error listing files: {errors}")
#                 return

#             for file_path in files:
#                 if not file_path or file_path in self.downloaded_files:
#                     continue

#                 sftp = ssh.open_sftp()
#                 try:
#                     attr = sftp.stat(file_path)
#                     modified_time = attr.st_mtime
#                     if modified_time < self.node_start_time:
#                         # self.get_logger().info(f"Skipping old file: {file_path}")
#                         sftp.close()
#                         continue

#                     file_name = os.path.basename(file_path)
#                     local_path = os.path.join(self.local_audio_dir, file_name)

#                     self.get_logger().info(f"New file found: {file_name}. Downloading...")
#                     sftp.get(file_path, local_path)
#                     self.get_logger().info(f"File {file_name} downloaded successfully to {local_path}.")
#                     self.downloaded_files.add(file_path)
#                     sftp.close()
#                     self.play_audio(local_path)

#                 except Exception as e:
#                     self.get_logger().error(f"Error processing file {file_path}: {e}")
#                     sftp.close()

        
#         except Exception as e:
#             self.get_logger().error(f"Error retrieving audio file: {e}")
#         finally:
#             ssh.close()


    
#     @contextlib.contextmanager
#     def suppress_gst_warnings():
#         with open(os.devnull, 'w') as devnull:
#             old_stdout = sys.stdout
#             old_stderr = sys.stderr
#             sys.stdout = devnull
#             sys.stderr = devnull
#             try:
#                 yield
#             finally:
#                 sys.stdout = old_stdout
#                 sys.stderr = old_stderr


#     def play_audio(self, file_path):
#         if os.path.exists(file_path):

#             msg_path = String()
#             msg_path.data = file_path
#             self.publisher_audio_path.publish(msg_path)
#             # self.get_logger().info(f"Full Time Taken from the begining of detecting a human speech to the start of giving a audio reponse to the user {time.time() - self.human_speech_detected_time}")
#             self.get_logger().info(f"Playing audio from {file_path}...")
#             time.sleep(0.1)
#             msg = Bool()  
#             msg.data = True
#             self.publisher_mouth_flag.publish(msg)
#             try:
#                 # with self.suppress_gst_warnings():  
#                 playsound(file_path)
#             except Exception as e:
#                 self.get_logger().error(f"Error playing audio: {e}")
#                 return
#             self.get_logger().info("Audio played successfully.")
#             msg.data = False
#             self.publisher_mouth_flag.publish(msg)
#             msg_end_reponse = Bool()
#             msg_end_reponse.data = True
#             self.publisher_end_audio_response.publish(msg_end_reponse)
#             self.get_logger().info(f"End audio reponse is, {msg_end_reponse}")

#         else:
#             self.get_logger().warn(f"Audio file not found at {file_path}.")



# def main(args=None):
#     rclpy.init(args=args)
#     node = AudioRetrievalNode()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == "__main__":
#     main()


##############################################################################

import rclpy
from rclpy.node import Node
import paramiko
import os
import time
from playsound import playsound
from std_msgs.msg import Bool, String, Int32, Empty
# from std_srvs.srv import Empty
from custom_interfaces.srv import MoveMouth
import contextlib
import sys


class AudioRetrievalNode(Node):
    def __init__(self):
        super().__init__('audio_retrieval_node')
        
        # Server details
        self.server_ip = "192.248.10.69"
        self.username = "fyp3-2"
        self.password = "cvpr*2022*BSMM"
        self.remote_audio_dir = "/home/fyp3-2/Desktop/Batch20/moshintha_ws/full_pipeline/version_2/audio_output_response_records"
        self.local_audio_dir = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios"
        self.downloaded_files = set()
        
        # Ensure the local directory exists
        if not os.path.exists(self.local_audio_dir):
            os.makedirs(self.local_audio_dir)

        # Timer to check for new audio files periodically
        self.timer = self.create_timer(0.5, self.retrieve_audio)  # Check every 500 ms second
        

        self.publisher_mouth_flag = self.create_publisher(Bool, 'mouth_flag', 10)
        self.publisher_audio_path = self.create_publisher(String, 'audio_response_path', 10)
        self.publisher_end_audio_response = self.create_publisher(Bool, 'end_audio_response', 10)
        self.response_start_pub = self.create_publisher(Empty, 'response_start', 10)

        self.subscriptions_unclear_audio = self.create_subscription(String, 'unclear_audio_path', self.unclear_audio_path_callback, 10)
        self.subscription_time = self.create_subscription(Int32, 'full_process_time', self.full_processing_time_callback, 10)
        self.subscription_filler_words_audio = self.create_subscription(String, 'filler_words_audio_path', self.filler_words_callback, 10)
        

        self.client = self.create_client(MoveMouth, 'audio_update')

        self.human_speech_detected_time = 0
        self.node_start_time = time.time()

        self.get_logger().info("Audio Retrieval Node has started.")

    def filler_words_callback(self, msg):
        filler_words_audio_path = msg.data
        # self.play_audio(filler_words_audio_path)

    def full_processing_time_callback(self, msg):
        self.human_speech_start_time = msg.data


    def unclear_audio_path_callback(self, msg):
        unclear_audio_path = msg.data
        self.play_audio(unclear_audio_path)


    def retrieve_audio(self):
        # self.get_logger().info("Checking server for new audio files...")
        # msg_end_reponse = Bool()
        # msg_end_reponse.data = False
        # self.publisher_end_audio_response.publish(msg_end_reponse)
        # self.get_logger().info(f"End audio reponse is, {msg_end_reponse}")

        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(self.server_ip, username=self.username, password=self.password)
            
            command = f"ls {self.remote_audio_dir}/*.wav 2>/dev/null"
            stdin, stdout, stderr = ssh.exec_command(command)
            files = stdout.read().decode().strip().split("\n")
            errors = stderr.read().decode().strip()

            if errors:
                self.get_logger().error(f"Error listing files: {errors}")
                return

            for file_path in files:
                if not file_path or file_path in self.downloaded_files:
                    continue

                sftp = ssh.open_sftp()
                try:
                    attr = sftp.stat(file_path)
                    modified_time = attr.st_mtime
                    if modified_time < self.node_start_time:
                        # self.get_logger().info(f"Skipping old file: {file_path}")
                        sftp.close()
                        continue

                    file_name = os.path.basename(file_path)
                    local_path = os.path.join(self.local_audio_dir, "output_audio.wav")

                    self.get_logger().info(f"New file found: {file_name}. Downloading...")
                    sftp.get(file_path, local_path)
                    self.get_logger().info(f"File {file_name} downloaded successfully to {local_path}.")
                    self.downloaded_files.add(file_path)
                    sftp.close()
                    self.play_audio(local_path)

                except Exception as e:
                    self.get_logger().error(f"Error processing file {file_path}: {e}")
                    sftp.close()

        
        except Exception as e:
            self.get_logger().error(f"Error retrieving audio file: {e}")
        finally:
            ssh.close()


    
    @contextlib.contextmanager
    def suppress_gst_warnings():
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = devnull
            sys.stderr = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr


    def play_audio(self, file_path):
        if os.path.exists(file_path):

            # msg_path = String()
            # msg_path.data = file_path
            # self.publisher_audio_path.publish(msg_path)
            # self.get_logger().info(f"Full Time Taken from the begining of detecting a human speech to the start of giving a audio reponse to the user {time.time() - self.human_speech_detected_time}")
            
            request = MoveMouth.Request()
            request.path = file_path
            self.get_logger().info('Service requesting!')
            future = self.client.call_async(request)
            self.get_logger().warn(request.path)
            # rclpy.spin_until_future_complete(self, future)
            
            count = 0
            # Wait for the future to complete
            while not future.done():
            # rclpy.spin_once(self)
                count += 1
                if count > 20:
                    self.get_logger().info("user id server is not responding")
                    # future.cancel()
                    break
                time.sleep(0.01)
            self.get_logger().info(f"Playing audio from {file_path}...")
            
            # time.sleep(0.1)
            if file_path == "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios/output_audio.wav":
                msg = Empty()  
                self.response_start_pub.publish(msg)
            try:
                # with self.suppress_gst_warnings():  
                playsound(file_path)
            except Exception as e:
                self.get_logger().error(f"Error playing audio: {e}")
                return
            self.get_logger().info("Audio played successfully.")
            
            
            # msg.data = False
            # self.publisher_mouth_flag.publish(msg)

            if file_path.startswith("/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/audio/thinking_audio_clips/"):
                pass
            else: 
                msg_end_reponse = Bool()
                msg_end_reponse.data = True
                self.publisher_end_audio_response.publish(msg_end_reponse)
                self.get_logger().info(f"End audio reponse is, {msg_end_reponse}")

        else:
            self.get_logger().warn(f"Audio file not found at {file_path}.")



def main(args=None):
    rclpy.init(args=args)
    node = AudioRetrievalNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
