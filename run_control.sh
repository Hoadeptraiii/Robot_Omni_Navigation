cd /home/thehoa/hospital_robot_nav
source install/setup.bash
ros2 run twist_stamper twist_stamper --ros-args -r cmd_vel_in:=/cmd_vel -r cmd_vel_out:=/mobile_base_controller/reference