cd /home/thehoa/hospital_robot_nav
source install/setup.bash
ros2 run nav2_map_server map_saver_cli -f src/nav2_simple_navigation/config/hospital_map
