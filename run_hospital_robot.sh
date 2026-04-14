cd /home/thehoa/hospital_robot_nav
colcon build --packages-select hospital_robot
cd /home/thehoa/hospital_robot_nav
source install/setup.bash
ros2 launch hospital_robot gazebo_control.launch.py