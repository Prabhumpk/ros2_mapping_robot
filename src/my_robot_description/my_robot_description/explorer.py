import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class Explorer(Node):
    def __init__(self):
        super().__init__('explorer')
        
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        self.timer = self.create_timer(
            0.1,
            self.move_robot
        )
        self.get_logger().info("Robot ready to explore")
        
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        self.front_distance = 999.0
        self.left_distancet = 999.0
        self.right_distance = 999.0
        self.counter = 0


    def move_robot(self):
        msg = Twist()
        if self.front_distance<1.2 :
            msg.linear.x = 0.0
            if self.left_distance > self.right_distance + 0.3:
                msg.angular.z = 1.0
            elif self.left_distance > self.left_distance + 0.3:
                msg.angular.z = -1.0
            else:
                msg.angular.z = 1.0
        elif self.left_distance < 0.4:
            msg.linear.x = 0.1
            msg.angular.z = -0.4
        elif self.right_distance < 0.4:
            msg.linear.x = 0.1
            msg.angular.z = 0.4
        else:
            msg.linear.x = 0.2
            msg.angular.z = 0.0
        self.cmd_pub.publish(msg)

    def scan_callback(self, msg):
        if len(msg.ranges) > 180:
            self.front_distance = msg.ranges[180]
            self.left_distance = msg.ranges[90]
            self.right_distance = msg.ranges[270]
            self.counter += 1
            if self.counter % 10 == 0:
                self.get_logger().info(
                    f"Front={self.front_distance:.2f} "
                    f"Left={self.left_distance:.2f} "
                    f"Right={self.right_distance:.2f}"
                )


    


def main(args=None):
    rclpy.init(args=args)
    node=Explorer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__=='__main__':
    main()