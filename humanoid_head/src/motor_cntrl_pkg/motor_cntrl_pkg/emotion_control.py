import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32MultiArray

class EmotionMotorController(Node):
    def __init__(self):
        super().__init__('emotion_motor_controller')

        self.subscription = self.create_subscription(
            String,
            '/current_emotion',
            self.emotion_callback,
            10
        )

        self.pos_publisher = self.create_publisher(Int32MultiArray, '/motor_pos', 10)
        self.speed_publisher = self.create_publisher(Int32MultiArray, '/motor_speed', 10)
#2,3,4,5,6,7,8,9,16,17,18,19,
        # Example lookup table: {emotion: [(channel, pos, vel), ...]}
        self.emotion_lookup = {                                                        
            'anger': [(2,959*4,12),(3,1511*4,12),(4,967*4,12),(5,1864*4,12),(6,1787*4,0),(7,1890*4,12),(8,919*4,12),(9,1032*4,12),(16,848*4,12),(17,1606*4,12),(18,1442*4,12),(19,1141*4,12)],
            'disgust': [(2,856*4,12),(3,1808*4,12),(4,1424*4,12),(5,1920*4,12),(6,1629*4,0),(7,1888*4,12),(8,1462*4,12),(9,1449*4,12),(16,927*4,12),(17,1339*4,12),(18,688*4,12),(19,1312*4,12)],
            'fear': [(2,959*4,12),(3,1511*4,12),(4,1314*4,12),(5,1920*4,12),(6,1445*4,12),(7,1890*4,12),(8,919*4,12),(9,1032*4,12),(16,1176*4,12),(17,1149*4,12),(18,688*4,12),(19,1410*4,12)],
            'joy': [(2,959*4,12),(3,1511*4,12),(4,967*4,12),(5,1864*4,12),(6,1787*4,0),(7,1890*4,12),(8,919*4,12),(9,1032*4,12),(16,848*4,12),(17,1606*4,12),(18,1442*4,12),(19,1141*4,12)],
            'neutral': [(2,972*4,12),(3,1334*4,12),(4,1269*4,12),(5,1830*4,12),(6,1629*4,0),(7,1918*4,12),(8,919*4,12),(9,1032*4,12),(16,848*4,12),(17,1606*4,12),(18,1442*4,12),(19,1141*4,12)],
            'sadness': [(2,959*4,12),(3,1361*4,12),(4,1369*4,12),(5,1809*4,12),(6,1457*4,12),(7,1942*4,12),(8,1309*4,12),(9,1032*4,12),(16,848*4,12),(17,1664*4,12),(18,688*4,12),(19,1507*4,12)],
            'surprise':[(2,959*4,12),(3,1511*4,12),(4,967*4,12),(5,1864*4,12),(6,1787*4,0),(7,1890*4,12),(8,919*4,12),(9,1032*4,12),(16,1201*4,12),(17,1064*4,12),(18,1486*4,12),(19,1507*4,12)]
        }

        self.get_logger().info("Emotion Motor Controller Node Started.")

    def emotion_callback(self, msg):
        emotion = msg.data.lower()
        if emotion not in self.emotion_lookup:
            self.get_logger().warn(f"Unknown emotion received: {emotion}")
            return

        motor_commands = self.emotion_lookup[emotion]
        for channel, position, velocity in motor_commands:
            self.publish_motor_pos(channel, position)
            self.publish_motor_speed(channel, velocity)


    def publish_motor_pos(self, channel, target_position):
        """Publishes the motor position to /motor_pos"""
        msg = Int32MultiArray()
        msg.data = [channel, target_position] 
        self.pos_publisher.publish(msg)
        self.get_logger().info(f"Published to /motor_pos: Channel {channel}, Position {target_position}")


    def publish_motor_speed(self,channel, velocity):
        """Publishes the motor speed to /motor_speed"""
        msg = Int32MultiArray()
        msg.data = [channel, velocity]  
        self.speed_publisher.publish(msg)
        self.get_logger().info(f"Published to /motor_speed: Channel {channel}, Speed {velocity}")
        

def main(args=None):
    rclpy.init(args=args)
    node = EmotionMotorController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
