#!/usr/bin/env python3
# import sys
# sys.path.append('/home/kuweni/ssd/conda/envs/tharusha/lib/python3.8/site-packages')

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int32
from geometry_msgs.msg import Point
from custom_interfaces.msg import People
from custom_interfaces.msg import PeopleArray
import time
import random
import math

class FaceTracker(Node):
    def __init__(self):
        super().__init__('face_tracker')

        # self.subscription = self.create_subscription(
        #     Point, "face_track", self.callback_face_track, 10)
        # self.subscription = self.create_subscription(Int32, "doa", self.doa_callback, 10)
        self.act_usrs_sub = self.create_subscription(PeopleArray,"active_users",self.active_usrs_callback,10)
        self.active_speaker_sub = self.create_subscription(People,"active_speaker",self.active_speaker_callback,10)
        
        self.pos_publisher = self.create_publisher(Int32MultiArray, '/motor_pos', 10)
        self.speed_publisher = self.create_publisher(Int32MultiArray, '/motor_speed', 10)
        self.tracking_timer = self.create_timer(0.1,self.face_track)


        self.right_eye_ver_chn = 10
        self.left_eye_ver_chn = 11
        self.right_eye_hor_chn = 12
        self.left_eye_hor_chn = 13

        self.right_hor_middle = 1330
        self.left_hor_middle = 1496.25 

        self.right_ver_middle = 1368
        self.left_ver_middle = 1210 

        self.neck_base_chn = 20
        self.neck_base_min = 992*4
        self.neck_base_max = 1968*4

        self.neck_top_chn = 21          # chsnnel no
        self.neck_top_min = 1136*4      # minimum limit
        self.neck_top_max = 1408*4      # maximum limit
        self.publish_motor_speed(self.neck_base_chn,8)

        self.horizontal_range = 120 # FOV 
        self.vertical_range = 360 

        self.horizontal_angle = 0 
        self.prev_horizontal_angle = 0

        self.verticle_angle = 0
        self.prev_verticle_angle = 0

        self.thr =5        # Publisher to send motor commands to /motor_pos
        self.speaker_id = 0
        self.speaker_name = ''

        self.active_usrs = []

        #blinking
        # self.timer = self.create_timer(random.uniform(3,4),self.blink_callback)

        self.get_logger().info("Eye Controller Node Started.")


    def active_speaker_callback(self, msg:People):
        self.speaker_id = msg.id
        self.speaker_name = msg.name

    def active_usrs_callback(self,msg:PeopleArray):
        self.active_usrs = msg.data
        if len(self.active_usrs) ==1:
            self.horizontal_angle = self.active_usrs[0].hor_angle
            self.verticle_angle = self.active_usrs[0].ver_angle

        for usr in self.active_usrs:
            if usr.id == self.speaker_id or usr.name == self.speaker_name:
                self.horizontal_angle = usr.hor_angle
                self.verticle_angle = usr.ver_angle
                break

        # self.face_track()

    def face_track(self):

        self.horizontal_tracking()
        self.verticle_tracking()

        # # self.horizontal_angle = (320 - msg.x)/640
        # delta_horizontal = self.horizontal_angle - self.prev_horizontal_angle

        # # self.verticle_angle = (msg.y - 180)/360

        # if (abs(delta_horizontal) < self.thr):
        #     # delta_horizontal = self.prev_horizontal_angle - self.horizontal_angle
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     # self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal)*4)
        #     # self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal)*4)

        # else:
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     # right_eye_horizontal = self.horizontal_angle  * 400 + 1576
        #     # left_eye_horizontal = self.horizontal_angle  * 528 + 1528
        #     # self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal)*4)
        #     # self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal)*4)
            
        #     self.publish_motor_speed(self.neck_base_chn,16)
        #     # self.publish_motor_speed(self.right_eye_hor_chn, 2)
        #     # self.publish_motor_speed(self.left_eye_hor_chn, 2)
        #     neck_horizontal =  self.horizontal_angle * (self.neck_base_max - self.neck_base_min)/self.horizontal_range + (self.neck_base_max + self.neck_base_min)/2  
        #     self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal))
        #     # time.sleep(0.250)
        #     # self.publish_motor_pos(self.right_eye_hor_chn, 1576*4)
        #     # self.publish_motor_pos(self.left_eye_hor_chn, 1528*4)


            
        #     self.prev_horizontal_angle = self.horizontal_angle
        #     self.publish_motor_speed(self.right_eye_hor_chn, 0)
        #     self.publish_motor_speed(self.left_eye_hor_chn, 0)


    def horizontal_tracking(self):
        delta_horizontal = self.horizontal_angle - self.prev_horizontal_angle
        if (abs(delta_horizontal) < self.thr):
            right_eye_horizontal = delta_horizontal * 6.67 + self.right_hor_middle
            left_eye_horizontal = delta_horizontal * 8.8 + self.left_hor_middle
            self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal*4))
            self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal*4))

        else:
            right_eye_horizontal = delta_horizontal * 6.67 + self.right_hor_middle
            left_eye_horizontal = delta_horizontal * 8.8 + self.left_hor_middle
            self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal*4))
            self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal*4))

            m_neck = 9.888
            c_neck = 1449.7958
            neck_base_pwm = m_neck * self.horizontal_angle + c_neck
            neck_base_pwm = int( neck_base_pwm * 4)
            if neck_base_pwm > self.neck_base_max:
                neck_base_pwm = self.neck_base_max 
            elif neck_base_pwm < self.neck_base_min:
                neck_base_pwm = self.neck_base_min
            
            self.publish_motor_pos(self.neck_base_chn,neck_base_pwm)
            self.publish_motor_pos(self.right_eye_hor_chn, int(self.right_hor_middle*4))
            self.publish_motor_pos(self.left_eye_hor_chn, int(self.left_hor_middle*4))
            self.prev_horizontal_angle = self.horizontal_angle
            

    def verticle_tracking(self):
        m_neck = -3.65
        c_neck = 1204.3399
        delta_ver = self.verticle_angle - self.prev_verticle_angle
        if (abs(delta_ver) < 1):
            self.prev_verticle_angle = self.verticle_angle
            return
        
        # if (abs(delta_ver) < self.thr):
        else:
            neck_top_pwm = m_neck * self.verticle_angle + c_neck
            neck_top_pwm = int( neck_top_pwm * 4)
            if neck_top_pwm > self.neck_top_max:    
                neck_top_pwm = self.neck_top_max
            elif neck_top_pwm < self.neck_top_min:
                neck_top_pwm = self.neck_top_min
            self.publish_motor_pos(self.neck_top_chn,neck_top_pwm)
            self.publish_motor_pos(self.right_eye_ver_chn, int(self.right_ver_middle*4))  
            self.publish_motor_pos(self.left_eye_ver_chn, int(self.left_ver_middle*4))


        # neck_verticle =self.verticle_angle * 212 + 720
        # self.publish_motor_speed(self.neck_top_chn,16)
        # self.publish_motor_pos(self.neck_top_chn,int(neck_verticle)*4) 
                           
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
        if (-40<msg.data<40):
            self.horizontal_angle = msg.data
            self.horizontal_tracking()
    #     if abs(self.horizontal_angle) >60:
    #         self.horizontal_angle = self.horizontal_angle/ abs(self.horizontal_angle)*60

    #     delta_horizontal = self.horizontal_angle - self.prev_horizontal_angle
    #     neck_horizontal =  self.horizontal_angle * (self.neck_base_max - self.neck_base_min)/self.horizontal_range + (self.neck_base_max + self.neck_base_min)/2  
    #     self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal))
    #     # time.sleep(0.250)
    #     self.publish_motor_pos(self.right_eye_hor_chn, 1576*4)
    #     self.publish_motor_pos(self.left_eye_hor_chn, 1528*4)

        # self.verticle_angle = (msg.y - 180)/360

        # if (abs(delta_horizontal) < self.thr):
        #     # delta_horizontal = self.prev_horizontal_angle - self.horizontal_angle
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal)*4)
        #     self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal)*4)

        # else:
        #     right_eye_horizontal = delta_horizontal * 400 + 1576
        #     left_eye_horizontal = delta_horizontal * 528 + 1528
        #     # right_eye_horizontal = self.horizontal_angle  * 400 + 1576
        #     # left_eye_horizontal = self.horizontal_angle  * 528 + 1528
        #     self.publish_motor_pos(self.right_eye_hor_chn, int(right_eye_horizontal)*4)
        #     self.publish_motor_pos(self.left_eye_hor_chn, int(left_eye_horizontal)*4)
            
        #     self.publish_motor_speed(self.neck_base_chn,16)
        #     self.publish_motor_speed(self.right_eye_hor_chn, 2)
        #     self.publish_motor_speed(self.left_eye_hor_chn, 2)
        #     neck_horizontal =  self.horizontal_angle * 496 + 1736  
        #     self.publish_motor_pos(self.neck_base_chn, int(neck_horizontal)*4)
        #     # time.sleep(0.250)
        #     self.publish_motor_pos(self.right_eye_hor_chn, 1576*4)
        #     self.publish_motor_pos(self.left_eye_hor_chn, 1528*4) 

            
        #     self.prev_horizontal_angle = self.horizontal_angle
        #     self.publish_motor_speed(self.right_eye_hor_chn, 0)
        #     self.publish_motor_speed(self.left_eye_hor_chn, 0)



def main(args=None):
    rclpy.init(args=args)
    node = FaceTracker() 
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()