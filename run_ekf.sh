cd /home/thehoa/hospital_robot_nav
colcon build --packages-select nav2_simple_navigation
source install/setup.bash
ros2 launch nav2_simple_navigation ekf.launch.py | grep ERROR