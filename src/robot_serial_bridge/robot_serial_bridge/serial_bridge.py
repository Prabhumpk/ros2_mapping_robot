#!/usr/bin/env python3

import serial
import threading

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Int32MultiArray


class SerialBridge(Node):

    def __init__(self):
        super().__init__('serial_bridge')

        self.port = '/dev/ttyUSB0'
        self.baudrate = 115200

        self.get_logger().info(
            f'Opening serial port {self.port}'
        )

        self.ser = serial.Serial(
            self.port,
            self.baudrate,
            timeout=0.1
        )

        self.cmd_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )

        self.encoder_pub = self.create_publisher(
            Int32MultiArray,
            '/encoder_counts',
            10
        )

        self.serial_thread = threading.Thread(
            target=self.read_serial_loop,
            daemon=True
        )

        self.serial_thread.start()

        self.get_logger().info(
            'Serial bridge started'
        )

    def cmd_vel_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        serial_msg = f"CMD,{linear:.3f},{angular:.3f}\n"

        self.ser.write(serial_msg.encode())

        self.get_logger().info(
            f"TX -> {serial_msg.strip()}"
        )

    def read_serial_loop(self):

        while rclpy.ok():

            try:

                line = (
                    self.ser.readline()
                    .decode()
                    .strip()
                )

                if not line:
                    continue

                self.get_logger().info(
                    f"RX <- {line}"
                )

                if line.startswith("ENC"):

                    parts = line.split(",")

                    if len(parts) == 3:

                        left = int(parts[1])
                        right = int(parts[2])

                        msg = Int32MultiArray()
                        msg.data = [left, right]

                        self.encoder_pub.publish(msg)

            except Exception as e:

                self.get_logger().error(
                    f"Serial error: {e}"
                )


def main(args=None):

    rclpy.init(args=args)

    node = SerialBridge()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()