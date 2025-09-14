#!/home/kuweni/ssd/conda/envs/tharusha/bin/python3

import rclpy
import serial
from std_msgs.msg import Int32MultiArray
from rclpy.node import Node
import time
from ts_py_pkg.maestro import Controller

class MaestroController(Node, Controller):  # Inherit from rclpy.node.Node
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        """Initialize the serial connection to the Maestro controller"""
        Node.__init__(self,'maestro_controller')  # Initialize the Node
        Controller.__init__(self)

        self.ser = serial.Serial(port, baudrate=baudrate, timeout=1)

        # ROS Subscriber to listen for position, velocity, and acceleration commands
        self.create_subscription(Int32MultiArray, "/motor_pos", self.pos_command_callback, 10)
        self.create_subscription(Int32MultiArray, "/motor_speed", self.speed_command_callback, 10)
        self.get_logger().info("Maestro Controller Node Started. Listening for commands on /motor_pos")

    # def set_target(self, channel, target):
    #     """
    #     Sends a command to set the servo target position.
    #     - channel: Servo channel number (0-23 for Maestro 24-channel)
    #     - target: Target position (in quarter-microseconds)
    #     """
    #     target_lsb = target & 0x7F
    #     target_msb = (target >> 7) & 0x7F
    #     command = bytearray([0x84, channel, target_lsb, target_msb])
    #     self.ser.write(command)
    #     self.get_logger().info(f"Set channel {channel} to position {target}")


    # def set_velocity(self, channel, velocity):
    #     """
    #     Sets the speed limit for the servo.
    #     - velocity: 0 (no limit) to 127 (slowest)
    #     """
    #     vel_lsb = velocity & 0x7F
    #     vel_msb = (velocity >> 7) & 0x7F
    #     command = bytearray([0x87, channel, vel_lsb, vel_msb])
    #     self.ser.write(command)
    #     self.get_logger().info(f"Set velocity {velocity} for channel {channel}")


    # def set_acceleration(self, channel, acceleration):
    #     """
    #     Sets the acceleration limit for the servo.
    #     - acceleration: 0 (no limit) to 255 (slowest)
    #     """
    #     acc_lsb = acceleration & 0x7F
    #     acc_msb = (acceleration >> 7) & 0x7F
    #     command = bytearray([0x89, channel, acc_lsb, acc_msb])
    #     self.ser.write(command)
    #     self.get_logger().info(f"Set acceleration {acceleration} for channel {channel}")


    def pos_command_callback(self, msg:Int32MultiArray):
        """Callback function triggered when a message is received on /motor_pos"""
        if len(msg.data) != 2:
            self.get_logger().warn("Invalid message format! Expecting [channel, position, velocity, acceleration].")
            return

        channel, target_position = msg.data
        self.get_logger().info(f"Received command: Channel {channel}, Pos {target_position}")

        self.setTarget(channel, target_position)
        time.sleep(0.01)


    def speed_command_callback(self, msg:Int32MultiArray):
        """Callback function triggered when a message is received on /motor_speed"""
        if len(msg.data) != 2:
            self.get_logger().warn("Invalid message format! Expecting [channel, position, velocity, acceleration].")
            return
        channel, velocity = msg.data
        self.get_logger().info(f"Received command: Channel {channel}, Vel {velocity}")
        self.setSpeed(channel, velocity)
        time.sleep(0.01)


    def close(self):
        """Closes the serial connection"""
        self.ser.close()



def main(args=None):
    rclpy.init(args=args)

    controller = MaestroController(port="/dev/ttyACM0")  # Update port if needed
    rclpy.spin(controller)
    controller.close()

if __name__ == "__main__":
    main()

