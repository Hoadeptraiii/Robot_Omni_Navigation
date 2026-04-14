cd /home/thehoa/hospital_robot_nav
source install/setup.bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true slam_params_file:=/home/thehoa/hospital_robot_nav/src/nav2_simple_navigation/config/mapper_params.yaml 
