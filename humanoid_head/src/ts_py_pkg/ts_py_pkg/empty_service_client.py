# file: empty_service_client.py

import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty

class SimpleClient(Node):
    def __init__(self):
        super().__init__('empty_service_client')
        self.client = self.create_client(Empty, 'trigger_action')

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')

        self.send_request()

    def send_request(self):
        request = Empty.Request()
        self.get_logger().info('Service requesting!')
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            self.get_logger().info('Service call succeeded!')
        else:
            self.get_logger().error('Service call failed.')

def main():
    rclpy.init()
    client_node = SimpleClient()
    rclpy.spin(client_node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
