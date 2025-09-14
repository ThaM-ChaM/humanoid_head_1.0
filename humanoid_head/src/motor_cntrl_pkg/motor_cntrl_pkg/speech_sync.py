#!/usr/bin/env python3
# /home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios/output_audio.wav
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32MultiArray, String, Empty
from std_srvs.srv import Empty
from custom_interfaces.srv import MoveMouth
import numpy as np
import wave
import random
from rclpy.timer import Timer
import time
import os

class MouthController(Node):
    def __init__(self):
        super().__init__('mouth_controller')

        # Publisher for /motor_pos topic
        self.pos_publisher = self.create_publisher(Int32MultiArray, '/motor_pos', 10)

        # Publisher for /motor_pos topic
        self.speed_publisher = self.create_publisher(Int32MultiArray, '/motor_speed', 10)

        # Handling the audio path request
        self.srv = self.create_service(MoveMouth, 'audio_update', self.audio_update_callback)

        # Blinking Timer
        interval = random.uniform(2, 4)  # Random interval between 2 to 4 seconds
        # self.blink_timer = self.create_timer(interval, self.blink_callback)

        self.audio_response_path = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios/output_audio.wav"
        self.wav_file = None
        self.frame_rate = None
        self.frames_per_step = None

        # Define eye lid servo channels
        self.upper_lid_channel = 14
        self.lower_lid_channel = 15

        self.publish_motor_speed(self.upper_lid_channel,0)
        self.publish_motor_speed(self.lower_lid_channel,0)

        # Define jaw servo channels
        self.left_jaw_channel = 0
        self.right_jaw_channel = 1

        self.publish_motor_speed(self.left_jaw_channel,0)
        self.publish_motor_speed(self.right_jaw_channel,0)

        # Define jaw open/close range
        self.left_jaw_min = 1296*4
        self.left_jaw_max = 1584*4
        self.right_jaw_min = 1712*4
        self.right_jaw_max = 1424*4
        
        self.mouth_open = False
        self.timer = None
        
        self.get_logger().info("Speech Sync Node Started.")
  

    def publish_motor_pos(self, channel, target_position):
        """Publishes the motor position to /motor_pos"""
        msg = Int32MultiArray()
        msg.data = [channel, target_position] 
        self.pos_publisher.publish(msg)
        self.get_logger().info(f"Published to /motor_pos: Channel {channel}, Position {target_position}")


    def publish_motor_speed(self, channel, target_speed):
        """Publishes the motor speed to /motor_pos"""
        msg = Int32MultiArray()
        msg.data = [channel, target_speed]  
        self.speed_publisher.publish(msg)
        self.get_logger().info(f"Published to /motor_speed: Channel {channel}, Speed {target_speed}")
    def blink_callback(self):
        self.publish_motor_pos(self.upper_lid_channel, 2032*4)
        self.publish_motor_pos(self.lower_lid_channel, 1584*4)
        time.sleep(0.2)
        self.publish_motor_pos(self.upper_lid_channel, 1200*4)
        self.publish_motor_pos(self.lower_lid_channel, 1120*4)
        self.blink_timer.cancel()
        interval = random.uniform(2, 4)
        self.blink_timer = self.create_timer(interval, self.blink_callback)


    def process_audio(self):
        if not self.mouth_open or not self.wav_file:
            return

        frames = self.wav_file.readframes(self.frames_per_step)
        if not frames:
            self.get_logger().info("Finished processing audio.")
            self.mouth_open = False
            self.mouth_timer.cancel()
            return

        audio_data = np.frombuffer(frames, dtype=np.int16)
        amplitude = np.abs(audio_data).mean()
        if (amplitude>4000):
            amplitude = 4000
        # self.wav_file.close()
        jaw_position = int(np.interp(amplitude, [0, 4000], [0, 100]))

        self.move_jaw(jaw_position)
    

    def move_jaw(self, jaw_position):
        left_jaw_pos = int(self.map_range(jaw_position, 0, 100, self.left_jaw_min, self.left_jaw_max))
        right_jaw_pos = int(self.map_range(jaw_position, 0, 100, self.right_jaw_min, self.right_jaw_max))

        self.publish_motor_pos(self.left_jaw_channel, left_jaw_pos)
        self.publish_motor_pos(self.right_jaw_channel, right_jaw_pos)


    def map_range(self, value, in_min, in_max, out_min, out_max):
        return out_min + (float(value - in_min) / float(in_max - in_min) * (out_max - out_min))
    

    def audio_update_callback(self, request: MoveMouth.Request, response: MoveMouth.Response):
        self.audio_response_path = request.path
        self.get_logger().warn(self.audio_response_path)

        try:
            if self.wav_file:
                self.wav_file.close()
            self.wav_file = wave.open(self.audio_response_path, 'rb')
            self.frame_rate = self.wav_file.getframerate()
            self.frames_per_step = self.frame_rate // 10
            self.get_logger().info(f"Loaded audio file: {self.audio_response_path}")
        except wave.Error as e:
            self.get_logger().error(f"Error opening WAV file: {e}")

        if not self.mouth_open and self.wav_file:
            self.mouth_open = True
            self.wav_file.rewind()  # Restart audio processing
            self.mouth_timer = self.create_timer(0.1, self.process_audio)  # 10Hz timer

        return response
        

def main(args=None):
    rclpy.init(args=args)
    node = MouthController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()




# #!/usr/bin/env python3
# # /home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios/output_audio.wav
# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import Bool, Int32MultiArray, String, Empty
# import numpy as np
# import wave
# import random
# from rclpy.timer import Timer
# import time
# import os

# class MouthController(Node):
#     def __init__(self):
#         super().__init__('mouth_controller')

#         # Subscribe to /mouth_flag topic
#         self.subscription = self.create_subscription(
#             Bool,
#             '/mouth_flag',
#             self.mouth_flag_callback,
#             10
#         )

#         # Subscribe to /audio_response_path topic (new!)
#         self.audio_response_path_subscription = self.create_subscription(
#             String,
#             '/audio_response_path',
#             self.audio_response_path_callback,
#             10
#         )

#         # #Sunscribe to /aduio_file_write topic
#         # self.audio_file_write_subscription = self.create_subscription(
#         #     Empty,
#         #     '/audio_file_write',
#         #     self.audio_response_path_callback,
#         #     10
#         # )

#         # Publisher for /motor_pos topic
#         self.pos_publisher = self.create_publisher(Int32MultiArray, '/motor_pos', 10)

#         # Blinking Timer
#         interval = random.uniform(2, 4)  # Random interval between 2 to 4 seconds
#         self.blink_timer = self.create_timer(interval, self.blink_callback)

#         self.wav_file = None
#         self.frame_rate = None
#         self.frames_per_step = None

#         # Define jaw servo channels
#         self.left_jaw_channel = 0
#         self.right_jaw_channel = 1

#         # Define jaw open/close range
#         self.left_jaw_min = 1408*4
#         self.left_jaw_max = 1584*4
#         self.right_jaw_min = 1600*4
#         self.right_jaw_max = 1424*4
        
#         self.mouth_open = False
#         self.timer = None
        
#         self.get_logger().info("Speech Sync Node Started.")
    
#     def audio_response_path_callback(self, msg):
#         # audio_response_path = "/home/kuweni/ssd/ros2_ws/src/robot_conversation_pipeline/robot_conversation_pipeline/retrieved_audios/output_audio.wav"
#         audio_response_path = msg.data
#         if not os.path.isfile(audio_response_path):
#             self.get_logger().error(f"Audio file not found: {audio_response_path}")
#             return

#         try:
#             if self.wav_file:
#                 self.wav_file.close()
#             self.wav_file = wave.open(audio_response_path, 'rb')
#             self.frame_rate = self.wav_file.getframerate()
#             self.frames_per_step = self.frame_rate // 10
#             self.get_logger().info(f"Loaded audio file: {audio_response_path}")
#         except wave.Error as e:
#             self.get_logger().error(f"Error opening WAV file: {e}")

#     def mouth_flag_callback(self, msg):
#         if msg.data and not self.mouth_open and self.wav_file:
#             self.mouth_open = True
#             self.wav_file.rewind()  # Restart audio processing
#             self.timer = self.create_timer(0.1, self.process_audio)  # 10Hz timer
#         elif not msg.data and self.mouth_open:
#             self.mouth_open = False
#             if self.timer:
#                 self.timer.cancel()  # Stop processing

#     def blink_callback(self):
#         self.publish_motor_pos(14, 2032*4)
#         self.publish_motor_pos(15, 1584*4)
#         time.sleep(0.2)
#         self.publish_motor_pos(14, 1200*4)
#         self.publish_motor_pos(15, 1120*4)
#         self.blink_timer.cancel()
#         interval = random.uniform(2, 4)
#         self.blink_timer = self.create_timer(interval, self.blink_callback)

#     def process_audio(self):
#         if not self.mouth_open or not self.wav_file:
#             return

#         frames = self.wav_file.readframes(self.frames_per_step)
#         if not frames:
#             self.get_logger().info("Finished processing audio.")
#             self.mouth_open = False
#             return

#         audio_data = np.frombuffer(frames, dtype=np.int16)
#         amplitude = np.abs(audio_data).mean()
#         if (amplitude>4000):
#             amplitude = 4000
#         # self.wav_file.close()
#         jaw_position = int(np.interp(amplitude, [0, 4000], [0, 100]))

#         self.move_jaw(jaw_position)
    
#     def move_jaw(self, jaw_position):
#         left_jaw_pos = int(self.map_range(jaw_position, 0, 100, self.left_jaw_min, self.left_jaw_max))
#         right_jaw_pos = int(self.map_range(jaw_position, 0, 100, self.right_jaw_min, self.right_jaw_max))

#         self.publish_motor_pos(self.left_jaw_channel, left_jaw_pos)
#         self.publish_motor_pos(self.right_jaw_channel, right_jaw_pos)

#     def publish_motor_pos(self, channel, target_position):
#         """Publishes the motor position to /motor_pos"""
#         msg = Int32MultiArray()
#         msg.data = [channel, target_position] 
#         self.pos_publisher.publish(msg)
#         self.get_logger().info(f"Published to /motor_pos: Channel {channel}, Position {target_position}")
    
#     def map_range(self, value, in_min, in_max, out_min, out_max):
#         return out_min + (float(value - in_min) / float(in_max - in_min) * (out_max - out_min))

# def main(args=None):
#     rclpy.init(args=args)
#     node = MouthController()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main()
