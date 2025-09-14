#!/home/kuweni/ssd/conda/envs/tharusha/bin/python3
import sys
sys.path.append('/home/kuweni/ssd/conda/envs/tharusha/lib/python3.8/site-packages')

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
from geometry_msgs.msg import Point
import time
import random
import math

class EyeController(Node):
    def __init__(self):
        super().__init__('eye_controller')

        self.subscription = self.create_subscription(
            Point, "face_track", self.callback_face_track, 10)
        self.subscription = self.create_subscription(
            Int32, "doa", self.doa_callback, 10)
        self.subscription  # prevent unused variable warning

        self.pos_publisher = self.create_publisher(Int32MultiArray, '/motor_pos', 10)
        self.speed_publisher = self.create_publisher(Int32MultiArray, '/motor_speed', 10)

        self.right_hor_chn = 10
        self.left_hor_chn = 11
        self.right_vir_chn = 12
        self.left_vir_chn = 13

        self.neck_base_chn = 20
        self.neck_base_min = 848*4
        self.neck_base_max = 1968*4

        self.neck_top_chn = 21
        self.neck_top_min = 1136*4
        self.neck_top_max = 1408*4
        self.publish_motor_speed(self.neck_base_chn,16)

        self.horizontal_range = 120 # FOV 
        self.vertical_range = 360 

        self.horizontal_angle = 0 
        self.prev_horizontal_angle = 0

        self.verticle_angle = 0
        
        self.thr = 0.1        # Publisher to send motor commands to /motor_pos


        #blinking
        # self.timer = self.create_timer(random.uniform(3,4),self.blink_callback)

        self.get_logger().info("Eye Controller Node Started.")


    def callback_face_track(self, msg:Point):

        self.horizontal_angle = (320 - msg.x)/640
        delta_horizontal = self.horizontal_angle - self.prev_horizontal_angle

        self.verticle_angle = (msg.y - 180)/360

        if (abs(delta_horizontal) < self.thr):
            # delta_horizontal = self.prev_horizontal_angle - self.horizontal_angle
            right_eye_horizontal = delta_horizontal * 400 + 1576
            left_eye_horizontal = delta_horizontal * 528 + 1528
            self.publish_motor_pos(self.right_hor_chn, int(right_eye_horizontal)*4)
            self.publish_motor_pos(self.left_hor_chn, int(left_eye_horizontal)*4)

        else:
            right_eye_horizontal = delta_horizontal * 400 + 1576
            left_eye_horizontal = delta_horizontal * 528 + 1528
            # right_eye_horizontal = self.horizontal_angle  * 400 + 1576
            # left_eye_horizontal = self.horizontal_angle  * 528 + 1528
            self.publish_motor_pos(self.right_hor_chn, int(right_eye_horizontal)*4)
            self.publish_motor_pos(self.left_hor_chn, int(left_eye_horizontal)*4)
            
            self.publish_motor_speed(self.neck_base_chn,16)
            self.publish_motor_speed(self.right_hor_chn, 2)
            self.publish_motor_speed(self.left_hor_chn, 2)
            neck_horizontal =  self.horizontal_angle * 496 + 1736  
            self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal)*4)
            # time.sleep(0.250)
            self.publish_motor_pos(self.right_hor_chn, 1576*4)
            self.publish_motor_pos(self.left_hor_chn, 1528*4) 

            
            self.prev_horizontal_angle = self.horizontal_angle
            self.publish_motor_speed(self.right_hor_chn, 0)
            self.publish_motor_speed(self.left_hor_chn, 0)

        self.verticle_tracking()

    def verticle_tracking(self):
        neck_verticle =self.verticle_angle * 212 + 720
        self.publish_motor_speed(self.neck_top_chn,16)
        self.publish_motor_pos(self.neck_top_chn,int(neck_verticle)*4) 
                           
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
        self.publish_motor_pos(14,2000*4)
        self.publish_motor_pos(15,1936*4)
        time.sleep(0.1)
        self.publish_motor_pos(14,1724*4)
        self.publish_motor_pos(15,1600*4)

        # Cancel existing timer if it exists
        if self.timer:
            self.timer.cancel()
        
        # Create a new timer
        self.timer = self.create_timer(random.uniform(3,4), self.blink_callback)

    def doa_callback(self,msg: Int32):

        self.horizontal_angle = msg.data
        if abs(self.horizontal_angle) >60:
            self.horizontal_angle = self.horizontal_angle/ abs(self.horizontal_angle)*60

        delta_horizontal = self.horizontal_angle - self.prev_horizontal_angle
        neck_horizontal =  self.horizontal_angle * (self.neck_base_max - self.neck_base_min)/self.horizontal_range + (self.neck_base_max + self.neck_base_min)/2  
        self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal))
        # time.sleep(0.250)
        self.publish_motor_pos(self.right_hor_chn, 1576*4)
        self.publish_motor_pos(self.left_hor_chn, 1528*4)

        # self.verticle_angle = (msg.y - 180)/360

        # if (abs(delta_horizontal) < self.thr):
        #     # delta_horizontal = self.prev_horizontal_angle - self.horizontal_angle
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     self.publish_motor_pos(self.right_hor_chn, int(right_eye_horizontal)*4)
        #     self.publish_motor_pos(self.left_hor_chn, int(left_eye_horizontal)*4)

        # else:
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     # right_eye_horizontal = self.horizontal_angle  * 400 + 1576
        #     # left_eye_horizontal = self.horizontal_angle  * 528 + 1528
        #     self.publish_motor_pos(self.right_hor_chn, int(right_eye_horizontal)*4)
        #     self.publish_motor_pos(self.left_hor_chn, int(left_eye_horizontal)*4)
            
        #     self.publish_motor_speed(self.neck_base_chn,16)
        #     self.publish_motor_speed(self.right_hor_chn, 2)
        #     self.publish_motor_speed(self.left_hor_chn, 2)
        #     neck_horizontal =  self.horizontal_angle * 496 + 1736  
        #     self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal)*4)
        #     # time.sleep(0.250)
        #     self.publish_motor_pos(self.right_hor_chn, 1576*4)
        #     self.publish_motor_pos(self.left_hor_chn, 1528*4) 

            
        #     self.prev_horizontal_angle = self.horizontal_angle
        #     self.publish_motor_speed(self.right_hor_chn, 0)
        #     self.publish_motor_speed(self.left_hor_chn, 0)



def main(args=None):
    rclpy.init(args=args)
    node = EyeController() 
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()