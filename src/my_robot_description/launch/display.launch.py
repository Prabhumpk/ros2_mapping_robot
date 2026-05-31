import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction

def generate_launch_description():
    # 1. Resolve package asset paths
    try:
        pkg_path = get_package_share_directory('my_robot_description')
    except KeyError:
        raise RuntimeError("Package 'my_robot_description' could not be located in the workspace.")

    urdf_file = os.path.join(pkg_path, 'urdf', 'my_robot.urdf')
    world_file = os.path.join(pkg_path, 'worlds', 'my_new_world.world')

    # 2. Extract and parse URDF data safely
    if not os.path.exists(urdf_file):
        raise FileNotFoundError(f"Target URDF structural file missing at: {urdf_file}")
        
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # 3. Define the Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )

    # 4. Define the Gazebo Physics Engine Process
    gazebo_process = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            world_file,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen'
    )

    # 5. Shield the spawning sequence behind a 5-second initialization timer
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'my_robot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen',
        parameters=[{'use_sim_time': True}],
        emulate_tty=True
    )

    delayed_spawn_action = TimerAction(
        period=5.0,
        actions=[spawn_robot_node]
    )

    # 6. Return orchestrated execution matrix
    return LaunchDescription([
        robot_state_publisher_node,
        gazebo_process,
        delayed_spawn_action
    ])