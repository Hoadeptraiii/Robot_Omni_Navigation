import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    pkg = get_package_share_directory('hospital_robot')

    urdf_file = os.path.join(pkg, 'urdf', 'omni_base.urdf')
    world_file = os.path.join(pkg, 'worlds','worlds', 'hospital_full.world')
    bridge_config = os.path.join(pkg, 'config', 'bridge_config.yaml')
    controller_config = os.path.join(pkg, 'config', 'configuration.yaml')
    pkg_parent_dir = os.path.join(pkg, '..')

    # Gazebo looks for models in GZ_SIM_RESOURCE_PATH, so we add the 'models' directory to it
    model_path = os.path.expanduser(
        '~/hospital_robot_nav/src/hospital_robot/worlds/models'
    )

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    # Thiết lập môi trường gazebo
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[pkg_parent_dir, ':', model_path]
    )
    
    # -------------------------
    # Controller YAML passed     # to gz_ros2_control
    # -------------------------
    set_ros_args = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_ARGS',
        value=f'--ros-args --params-file {controller_config}'
    )

    # -------------------------
    # Robot State Publisher
    # -------------------------

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # -------------------------
    # Start Gazebo
    # -------------------------

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    # -------------------------
    # Spawn robot
    # -------------------------

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'omni_base',
            '-x', '0.0',
            '-y', '12',
            '-z', '0.0',
            '-Y', '-1.57'
        ],
        output='screen'
    )

   

    # -------------------------
    # ROS <-> Gazebo Bridge
    # Uses bridge_config.yaml
    # -------------------------

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': bridge_config,
                     'use_sim_time': use_sim_time}],
        output='screen'
    )

    # -------------------------
    # ros2_control Controllers
    # -------------------------

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'joint_state_broadcaster',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    mobile_base_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            'mobile_base_controller',
            '--controller-manager',
            '/controller_manager'
        ],
        output='screen'
    )

    # imu_broadcaster = Node(
    #     package='controller_manager',
    #     executable='spawner',
    #     arguments=[
    #         'imu_sensor_broadcaster',
    #         '--controller-manager',
    #         '/controller_manager'
    #     ],
    #     output='screen'
    # )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        # Nếu bạn có file cấu hình rviz (.rviz), hãy thêm dòng dưới:
        # arguments=['-d', os.path.join(pkg, 'rviz', 'sensor_view.rviz')]
    )

    # -------------------------
    # Node ekf
    # -------------------------
    # robot_localization_node = Node(
    #     package='robot_localization',
    #     executable='ekf_node',
    #     name='ekf_filter_node',
    #     output='screen',
    #     parameters=[os.path.join(pkg, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    # )

    # --- Sắp xếp thứ tự chạy bằng TimerAction ---
    delayed_spawn = TimerAction(
        period= 20.0,
        actions=[spawn_robot]
    )

    delayed_bridge = TimerAction(
        period=5.0,
        actions=[bridge]
    )

    delayed_controllers = TimerAction(
        period=8.0,
        actions=[
            joint_state_broadcaster,
            mobile_base_controller
        ]
    )


    # -------------------------
    # Launch everything
    # -------------------------

    return LaunchDescription([
        declare_use_sim_time,
        set_gz_resource_path,
        set_ros_args,
        robot_state_publisher,
        gz_sim,
        delayed_spawn,
        delayed_bridge,
        delayed_controllers,
        rviz_node,
    ])