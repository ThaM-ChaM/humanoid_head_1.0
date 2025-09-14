
import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty

class SimpleServer(Node):
    def __init__(self):
        super().__init__('empty_service_server')
        self.srv = self.create_service(Empty, 'trigger_action', self.handle_trigger)

    def handle_trigger(self, request, response):
        self.get_logger().info('Service was called!')
        return response  # No data to return, just send the empty response

def main():
    rclpy.init()
    node = SimpleServer()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
