import rclpy
from rclpy.node import Node
import time
from example_interfaces.srv import AddTwoInts

class MyAsyncClient(Node):

    def __init__(self):
        super().__init__('my_async_client')
        self.cli = self.create_client(AddTwoInts, 'add_two_ints')

    def send_request(self, a, b):
        # while not self.cli.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('Waiting for service...')
        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        future = self.cli.call_async(request)
        count = 0
        # Wait for the future to complete
        while not future.done():
            # rclpy.spin_once(self)
            count += 1
            if count > 10:
                self.get_logger().info("user id server is not responding")
                future.cancel()
                break
            time.sleep(0.01)

def main(args=None):
    rclpy.init()
    node = MyAsyncClient() 
    node.send_request(1, 2)
    rclpy.spin(node)
    rclpy.shutdown()
 
 
if __name__ == "__main__":
    main()