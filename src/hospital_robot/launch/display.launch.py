from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch_ros.actions import ComposableNodeContainer
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import DeclareLaunchArgument
# Nếu dùng ros_gz_bridge dạng class
from ros_gz_bridge.actions import RosGzBridge


def generate_launch_description():

    pkg_path = get_package_share_directory('hospital_robot')

    urdf_path = os.path.join(pkg_path, 'urdf', 'omni_base.urdf')
    bridge_config_path = os.path.join(pkg_path, 'config', 'bridge_config.yaml')
    world_path = os.path.join(pkg_path, 'worlds', 'worlds', 'hospital_aws.world')

    # Gazebo spawn launch
    gz_spawn_model_launch_source = os.path.join(
        get_package_share_directory('ros_gz_sim'),
        'launch',
        'gz_spawn_model.launch.py'
    )

    # đọc URDF
    with open(urdf_path, 'r') as infp:
        robot_description = infp.read()

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),

        # 🔹 Robot State Publisher (publish TF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': LaunchConfiguration('use_sim_time')
            }],
            output='screen'
        ),

        # 🔹 Joint State Publisher GUI
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen'
        ),

        # 🔹 RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        ),

        # 🔹 ROS ↔ Gazebo Bridge
        RosGzBridge(
            bridge_name='ros_gz_bridge',
            config_file=bridge_config_path,
            container_name='ros_gz_container',
            create_own_container='False',
            use_composition='True',
        ),

         Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[os.path.join(pkg_path, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        # 🔹 Spawn robot vào Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_spawn_model_launch_source),
            launch_arguments={
                'world': 'hospital_aws.world',
                'topic': '/robot_description',
                'entity_name': 'hospital_robot',
                'z': '0.65',
            }.items(),
        ),

        

    ])