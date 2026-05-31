from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import TimerAction
TimerAction(
    period=5.0,
    actions=[
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-entity', 'my_robot',
                '-topic', 'robot_description',
                '-x', '0',
                '-y', '0',
                '-z', '0.5'
            ],
            output='screen'
        )
    ]
)

def generate_launch_description():

    pkg_path = get_package_share_directory('my_robot_description')

    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf')

    world_file = os.path.join(pkg_path, 'worlds', 'my_world.world')

    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    return LaunchDescription([
        Node(
             package='joint_state_publisher',
             executable='joint_state_publisher',
             name='joint_state_publisher',
             output='screen'
        ),
        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_desc
            }],
            output='screen'
        ),

        # Gazebo
       ExecuteProcess(
    cmd=[
        'gazebo',
        '--verbose',
        world_file,
        '-s',
        'libgazebo_ros_init.so',
        '-s',
        'libgazebo_ros_factory.so'
    ],
    output='screen'
),

        # Spawn Robot
        Node(
    package='gazebo_ros',
    executable='spawn_entity.py',
    arguments=[
        '-entity', 'my_robot',
        '-topic', 'robot_description',
        '-x', '0',
        '-y', '0',
        '-z', '0.5'
    ],
    output='screen',
    parameters=[{'use_sim_time': True}],
    emulate_tty=True
)
    ])
