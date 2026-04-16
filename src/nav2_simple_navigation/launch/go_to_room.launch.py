from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav2_simple_navigation',
            executable='go_to_room',  # phải đúng với entry_points trong setup.py
            name='room_navigator',
            output='screen',
            emulate_tty=True,
            parameters=[{
                'use_sim_time': True  # True nếu chạy Gazebo
            }]
        )
    ])