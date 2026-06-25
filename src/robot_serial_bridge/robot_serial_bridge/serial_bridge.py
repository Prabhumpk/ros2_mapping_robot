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

        self.serial_connected = False

        self.left_encoder = 0
        self.right_encoder = 0

        self.get_logger().info(
            f'Trying to open {self.port}'
        )

        try:

            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=0.1
            )

            self.serial_connected = True

            self.get_logger().info(
                f'Connected to {self.port}'
            )

        except Exception as e:

            self.get_logger().warn(
                f'Serial not available. Running in TEST MODE. {e}'
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

        self.encoder_timer = self.create_timer(
            0.1,
            self.publish_test_encoder
        )

        if self.serial_connected:

            self.serial_thread = threading.Thread(
                target=self.read_serial_loop,
                daemon=True
            )

            self.serial_thread.start()

        self.get_logger().info(
            'Serial Bridge Started'
        )

    def cmd_vel_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        serial_msg = (
            f"CMD,{linear:.3f},{angular:.3f}\n"
        )

        if self.serial_connected:

            try:

                self.ser.write(
                    serial_msg.encode()
                )

            except Exception as e:

                self.get_logger().error(
                    f"Serial Write Error: {e}"
                )

        self.get_logger().info(
            f"TX -> {serial_msg.strip()}"
        )

    def publish_test_encoder(self):

        if self.serial_connected:
            return

        self.left_encoder += 5
        self.right_encoder += 5

        msg = Int32MultiArray()
        msg.data = [
            self.left_encoder,
            self.right_encoder
        ]

        self.encoder_pub.publish(msg)

    def read_serial_loop(self):

        while rclpy.ok():

            try:

                line = (
                    self.ser.readline()
                    .decode(errors='ignore')
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

                        msg.data = [
                            left,
                            right
                        ]

                        self.encoder_pub.publish(
                            msg
                        )

            except Exception as e:

                self.get_logger().error(
                    f"Serial Read Error: {e}"
                )

    def destroy_node(self):

        if self.serial_connected:

            try:
                self.ser.close()

            except:
                pass

        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = SerialBridge()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()