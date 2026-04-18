#  🏥 Hospital Robot Navigation (ROS2 Jazzy)
Dự án điều hướng robot thông minh trong bệnh viện, chạy trên nền tảng Ubuntu 24.04 và ROS 2 Jazzy Jalisco. Hệ thống cho phép robot di chuyển chính xác đến các phòng bệnh thông qua tọa độ định sẵn.
## 👥 Thành viên nhóm

|      Name      | Student ID |
| :------------: | :--------: |
|   Lê Thế Hòa   |  23134023  |
| Nguyễn Văn Nam |  23134038  |
|  Hồ Quốc Việt  |  23134065  |

## Yêu cầu hệ thống
HĐH: Ubuntu 24.04 LTS  
ROS 2: Jazzy Jalisco  
Mô phỏng: Gazebo Harmonic / Ignition  
Python 3.12+
## Cài đặt
git clone https://github.com/Hoadeptraiii/Robot_Omni_Navigation.git   
cd Robot_Omni_Navigation  
## Cấu trúc thư mục
---

```bash
Robot_Omni_Navigation/
├── README.md
├── run_ekf.sh
├── run_hospital_robot.sh
├── run_slam.sh
├── save_map.sh
└── src/
    ├── hospital_robot/
    │   ├── CMakeLists.txt
    │   ├── config/
    │   │   ├── bridge_config.yaml
    │   │   └── configuration.yaml
    │   ├── launch/
    │   │   ├── display.launch.py
    │   │   └── gazebo_control.launch.py
    │   ├── package.xml
    │   ├── scripts/
    │   ├── urdf/
    │   │   └── omni_base.urdf
    │   └── worlds/
    │       ├── empty.sdf
    │       ├── models/
    │       └── worlds/
    └── nav2_simple_navigation/
        ├── CMakeLists.txt
        ├── config/
        │   ├── ekf.yaml
        │   ├── hospital_map.pgm
        │   ├── hospital_map.yaml
        │   ├── mapper_params.yaml
        │   ├── nav2_hospital_params.yaml
        │   ├── nav2_params.yaml
        │   ├── nav2_params_wo_BT.yaml
        │   ├── navigate_to_pose_w_replanning_and_recovery.xml
        │   └── rooms.yaml
        ├── launch/
        │   ├── ekf.launch.py
        │   ├── go_to_room.launch.py
        │   ├── nav2_control.launch.py
        │   └── navigation2.launch.py
        ├── nav2_simple_navigation/
        │   ├── __init__.py
        │   ├── map.png
        │   └── navigation_gui.py
        ├── package.xml
        ├── resource/
        │   └── nav2_simple_navigation
        ├── rviz/
        │   └── tb3_navigation2.rviz
        ├── setup.cfg
        └── setup.py
```

---

## Sử dụng
Sửa các đường link tại các file thành đường link của bạn:  
-Dòng 770 file omni_base.urdf:     <parameters>/home/thehoa/hospital_robot_nav/install/hospital_robot/share/hospital_robot/config/configuration.yaml</parameters>   
-Sửa dòng đầu của file run_hospital_robot.sh: cd /home/thehoa/hospital_robot_nav  
Lần lượt chạy các câu lệnh sau để có thể sử dụng mã nguồn:  
1. Ctr+'~' để mở terminal và chạy: ./run_hospital_robot.sh  
2. Mở thêm 1 terminal mới:  
    colcon build --symlink-instal  
    source install/setup.bash  
    ros2 launch nav2_simple_navigation navigation2.launch.py   
3. Chạy file: navigation_gui.py  

