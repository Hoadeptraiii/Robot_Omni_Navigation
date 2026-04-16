# import math
# import yaml
# import rclpy
# from rclpy.node import Node
# from rclpy.action import ActionClient
# from nav2_msgs.action import NavigateToPose

# YAML_PATH = '/home/viet/hospital_robot_nav/src/nav2_simple_navigation/config/rooms.yaml'


# def euler_to_quaternion(yaw: float) -> tuple:
#     """Chuyển góc yaw (radian) sang quaternion (x, y, z, w)."""
#     half = yaw / 2
#     return (0.0, 0.0, math.sin(half), math.cos(half))


# class RoomNavigator(Node):
#     def __init__(self):
#         super().__init__('room_navigator')
#         self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

#         with open(YAML_PATH, 'r') as f:
#             self.rooms = yaml.safe_load(f)['rooms']
#         self.get_logger().info(f"Đã tải {len(self.rooms)} phòng.")

#     def _build_goal(self, pose: dict) -> NavigateToPose.Goal:
#         """Tạo goal từ dict có khóa x, y, yaw."""
#         goal = NavigateToPose.Goal()
#         goal.pose.header.frame_id = 'map'
#         goal.pose.header.stamp = self.get_clock().now().to_msg()
#         goal.pose.pose.position.x = float(pose['x'])
#         goal.pose.pose.position.y = float(pose['y'])
#         qx, qy, qz, qw = euler_to_quaternion(float(pose.get('yaw', 0.0)))
#         goal.pose.pose.orientation.x = qx
#         goal.pose.pose.orientation.y = qy
#         goal.pose.pose.orientation.z = qz
#         goal.pose.pose.orientation.w = qw
#         return goal

#     def navigate_to(self, pose: dict, label: str = '') -> bool:
#         """Gửi goal đến Nav2 và chờ robot đến nơi. Trả về True nếu thành công."""
#         self.get_logger().info(f"Đang di chuyển đến {label}: x={pose['x']}, y={pose['y']}")
#         self._client.wait_for_server()

#         future = self._client.send_goal_async(self._build_goal(pose))
#         rclpy.spin_until_future_complete(self, future)
#         handle = future.result()

#         if not handle.accepted:
#             self.get_logger().error("Goal bị từ chối!")
#             return False

#         result_future = handle.get_result_async()
#         rclpy.spin_until_future_complete(self, result_future)
#         return True

#     def go_to_room(self, room_num: str):
#         """Điều hướng robot đến cửa rồi vào giữa phòng."""
#         room_id = f'room_{room_num}'
#         if room_id not in self.rooms:
#             print(f"❌ Không tìm thấy phòng: {room_num}")
#             return

#         room = self.rooms[room_id]

#         print(f"🚀 [1/3] Đến cửa phòng {room_num}...")
#         if not self.navigate_to(room['door'], f"cửa phòng {room_num}"):
#             return
        
#         print(f"🚀 [2/3] sau phòng {room_num}...")
#         if self.navigate_to(room['inside'], f"giữa phòng {room_num}"):
#             print(f"🏁 Hoàn thành! Robot đang ở trong phòng {room_num}.")

#         print(f"🚀 [3/3] Vào giữa phòng {room_num}...")
#         if self.navigate_to(room['center'], f"giữa phòng {room_num}"):
#             print(f"🏁 Hoàn thành! Robot đang ở trong phòng {room_num}.")

   

# def main():
#     rclpy.init()
#     navigator = RoomNavigator()

#     print('\n--- HỆ THỐNG ĐIỀU HƯỚNG ROBOT BỆNH VIỆN ---')
#     while rclpy.ok():
#         try:
#             user_input = input("\nNhập số phòng (vd: 101) hoặc 'exit' để thoát: ").strip()
#             if user_input.lower() == 'exit':
#                 break
#             if user_input:
#                 navigator.go_to_room(user_input)
#         except KeyboardInterrupt:
#             break

#     navigator.destroy_node()


# if __name__ == '__main__':
#     main()

import math
import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

YAML_PATH = '/home/viet/hospital_robot_nav/src/nav2_simple_navigation/config/rooms.yaml'


def euler_to_quaternion(yaw: float) -> tuple:
    half = yaw / 2
    return (0.0, 0.0, math.sin(half), math.cos(half))


def reverse_yaw(yaw: float) -> float:
    new_yaw = yaw + math.pi
    return math.atan2(math.sin(new_yaw), math.cos(new_yaw))


class RoomNavigator(Node):
    def __init__(self):
        super().__init__('room_navigator')

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        with open(YAML_PATH, 'r') as f:
            self.rooms = yaml.safe_load(f)['rooms']

        self.current_room = None  # ✅ thêm dòng này

        self.get_logger().info(f"Đã tải {len(self.rooms)} phòng.")

    def reverse_pose(self, pose: dict) -> dict:
        return {
            'x': pose['x'],
            'y': pose['y'],
            'yaw': reverse_yaw(float(pose.get('yaw', 0.0)))
        }

    def _build_goal(self, pose: dict) -> NavigateToPose.Goal:
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = float(pose['x'])
        goal.pose.pose.position.y = float(pose['y'])

        qx, qy, qz, qw = euler_to_quaternion(float(pose.get('yaw', 0.0)))
        goal.pose.pose.orientation.x = qx
        goal.pose.pose.orientation.y = qy
        goal.pose.pose.orientation.z = qz
        goal.pose.pose.orientation.w = qw

        return goal

    def navigate_to(self, pose: dict, label: str = '') -> bool:
        self.get_logger().info(
            f"➡️ {label}: x={pose['x']:.2f}, y={pose['y']:.2f}"
        )

        self._client.wait_for_server()

        future = self._client.send_goal_async(self._build_goal(pose))
        rclpy.spin_until_future_complete(self, future)
        handle = future.result()

        if not handle.accepted:
            self.get_logger().error("❌ Goal bị từ chối!")
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        return True

    def go_to_room(self, room_num: str):
        room_id = f'room_{room_num}'

        if room_id not in self.rooms:
            print(f"❌ Không tìm thấy phòng: {room_num}")
            return

        # ✅ tránh đi lại cùng phòng
        if self.current_room == room_num:
            print("⚠️ Robot đã ở phòng này rồi!")
            return

        target_room = self.rooms[room_id]

        print(f"\n📍 Phòng hiện tại: {self.current_room}")
        print(f"➡️ Đang đi đến phòng: {room_num}")

        # =========================
        # 🟥 1. THOÁT PHÒNG HIỆN TẠI
        # =========================
        if self.current_room is not None:
            current_id = f'room_{self.current_room}'
            current_room = self.rooms[current_id]

            print(f"🔙 Thoát phòng {self.current_room}...")

            # center -> inside (quay đầu)
            inside_rev = self.reverse_pose(current_room['inside'])
            if not self.navigate_to(inside_rev, f"thoát inside phòng {self.current_room}"):
                return

            # inside -> door (quay đầu)
            door_rev = self.reverse_pose(current_room['door'])
            if not self.navigate_to(door_rev, f"thoát cửa phòng {self.current_room}"):
                return

        # =========================
        # 🟩 2. ĐI ĐẾN PHÒNG MỚI
        # =========================
        print(f"🚀 [1/3] Đến cửa phòng {room_num}...")
        if not self.navigate_to(target_room['door'], f"cửa phòng {room_num}"):
            return

        print(f"🚀 [2/3] Vào trong phòng {room_num}...")
        if not self.navigate_to(target_room['inside'], f"trong phòng {room_num}"):
            return

        print(f"🚀 [3/3] Đến trung tâm phòng {room_num}...")
        if self.navigate_to(target_room['center'], f"trung tâm phòng {room_num}"):
            self.current_room = room_num
            print(f"🏁 Hoàn thành! Robot đang ở phòng {room_num}.")


def main():
    rclpy.init()
    navigator = RoomNavigator()

    print('\n--- HỆ THỐNG ĐIỀU HƯỚNG ROBOT BỆNH VIỆN ---')

    while rclpy.ok():
        try:
            user_input = input("\nNhập số phòng (vd: 5) hoặc 'exit': ").strip()

            if user_input.lower() == 'exit':
                break

            if user_input:
                navigator.go_to_room(user_input)

        except KeyboardInterrupt:
            break

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()# import math
# import yaml
# import rclpy
# from rclpy.node import Node
# from rclpy.action import ActionClient
# from nav2_msgs.action import NavigateToPose

# YAML_PATH = '/home/viet/hospital_robot_nav/src/nav2_simple_navigation/config/rooms.yaml'


# def euler_to_quaternion(yaw: float) -> tuple:
#     """Chuyển góc yaw (radian) sang quaternion (x, y, z, w)."""
#     half = yaw / 2
#     return (0.0, 0.0, math.sin(half), math.cos(half))


# class RoomNavigator(Node):
#     def __init__(self):
#         super().__init__('room_navigator')
#         self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

#         with open(YAML_PATH, 'r') as f:
#             self.rooms = yaml.safe_load(f)['rooms']
#         self.get_logger().info(f"Đã tải {len(self.rooms)} phòng.")

#     def _build_goal(self, pose: dict) -> NavigateToPose.Goal:
#         """Tạo goal từ dict có khóa x, y, yaw."""
#         goal = NavigateToPose.Goal()
#         goal.pose.header.frame_id = 'map'
#         goal.pose.header.stamp = self.get_clock().now().to_msg()
#         goal.pose.pose.position.x = float(pose['x'])
#         goal.pose.pose.position.y = float(pose['y'])
#         qx, qy, qz, qw = euler_to_quaternion(float(pose.get('yaw', 0.0)))
#         goal.pose.pose.orientation.x = qx
#         goal.pose.pose.orientation.y = qy
#         goal.pose.pose.orientation.z = qz
#         goal.pose.pose.orientation.w = qw
#         return goal

#     def navigate_to(self, pose: dict, label: str = '') -> bool:
#         """Gửi goal đến Nav2 và chờ robot đến nơi. Trả về True nếu thành công."""
#         self.get_logger().info(f"Đang di chuyển đến {label}: x={pose['x']}, y={pose['y']}")
#         self._client.wait_for_server()

#         future = self._client.send_goal_async(self._build_goal(pose))
#         rclpy.spin_until_future_complete(self, future)
#         handle = future.result()

#         if not handle.accepted:
#             self.get_logger().error("Goal bị từ chối!")
#             return False

#         result_future = handle.get_result_async()
#         rclpy.spin_until_future_complete(self, result_future)
#         return True

#     def go_to_room(self, room_num: str):
#         """Điều hướng robot đến cửa rồi vào giữa phòng."""
#         room_id = f'room_{room_num}'
#         if room_id not in self.rooms:
#             print(f"❌ Không tìm thấy phòng: {room_num}")
#             return

#         room = self.rooms[room_id]

#         print(f"🚀 [1/3] Đến cửa phòng {room_num}...")
#         if not self.navigate_to(room['door'], f"cửa phòng {room_num}"):
#             return
        
#         print(f"🚀 [2/3] sau phòng {room_num}...")
#         if self.navigate_to(room['inside'], f"giữa phòng {room_num}"):
#             print(f"🏁 Hoàn thành! Robot đang ở trong phòng {room_num}.")

#         print(f"🚀 [3/3] Vào giữa phòng {room_num}...")
#         if self.navigate_to(room['center'], f"giữa phòng {room_num}"):
#             print(f"🏁 Hoàn thành! Robot đang ở trong phòng {room_num}.")

   

# def main():
#     rclpy.init()
#     navigator = RoomNavigator()

#     print('\n--- HỆ THỐNG ĐIỀU HƯỚNG ROBOT BỆNH VIỆN ---')
#     while rclpy.ok():
#         try:
#             user_input = input("\nNhập số phòng (vd: 101) hoặc 'exit' để thoát: ").strip()
#             if user_input.lower() == 'exit':
#                 break
#             if user_input:
#                 navigator.go_to_room(user_input)
#         except KeyboardInterrupt:
#             break

#     navigator.destroy_node()


# if __name__ == '__main__':
#     main()

import math
import yaml
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

YAML_PATH = '/home/thehoa/hospital_robot_nav/src/nav2_simple_navigation/config/rooms.yaml'


def euler_to_quaternion(yaw: float) -> tuple:
    half = yaw / 2
    return (0.0, 0.0, math.sin(half), math.cos(half))


def reverse_yaw(yaw: float) -> float:
    new_yaw = yaw + math.pi
    return math.atan2(math.sin(new_yaw), math.cos(new_yaw))


class RoomNavigator(Node):
    def __init__(self):
        super().__init__('room_navigator')

        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        with open(YAML_PATH, 'r') as f:
            self.rooms = yaml.safe_load(f)['rooms']

        self.current_room = None  # ✅ thêm dòng này

        self.get_logger().info(f"Đã tải {len(self.rooms)} phòng.")

    def reverse_pose(self, pose: dict) -> dict:
        return {
            'x': pose['x'],
            'y': pose['y'],
            'yaw': reverse_yaw(float(pose.get('yaw', 0.0)))
        }

    def _build_goal(self, pose: dict) -> NavigateToPose.Goal:
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        goal.pose.pose.position.x = float(pose['x'])
        goal.pose.pose.position.y = float(pose['y'])

        qx, qy, qz, qw = euler_to_quaternion(float(pose.get('yaw', 0.0)))
        goal.pose.pose.orientation.x = qx
        goal.pose.pose.orientation.y = qy
        goal.pose.pose.orientation.z = qz
        goal.pose.pose.orientation.w = qw

        return goal

    def navigate_to(self, pose: dict, label: str = '') -> bool:
        self.get_logger().info(
            f"➡️ {label}: x={pose['x']:.2f}, y={pose['y']:.2f}"
        )

        self._client.wait_for_server()

        future = self._client.send_goal_async(self._build_goal(pose))
        rclpy.spin_until_future_complete(self, future)
        handle = future.result()

        if not handle.accepted:
            self.get_logger().error("❌ Goal bị từ chối!")
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        return True

    def go_to_room(self, room_num: str):
        room_id = f'room_{room_num}'

        if room_id not in self.rooms:
            print(f"❌ Không tìm thấy phòng: {room_num}")
            return

        # ✅ tránh đi lại cùng phòng
        if self.current_room == room_num:
            print("⚠️ Robot đã ở phòng này rồi!")
            return

        target_room = self.rooms[room_id]

        print(f"\n📍 Phòng hiện tại: {self.current_room}")
        print(f"➡️ Đang đi đến phòng: {room_num}")

        # =========================
        # 🟥 1. THOÁT PHÒNG HIỆN TẠI
        # =========================
        if self.current_room is not None:
            current_id = f'room_{self.current_room}'
            current_room = self.rooms[current_id]

            print(f"🔙 Thoát phòng {self.current_room}...")

            # center -> inside (quay đầu)
            inside_rev = self.reverse_pose(current_room['inside'])
            if not self.navigate_to(inside_rev, f"thoát inside phòng {self.current_room}"):
                return

            # inside -> door (quay đầu)
            door_rev = self.reverse_pose(current_room['door'])
            if not self.navigate_to(door_rev, f"thoát cửa phòng {self.current_room}"):
                return

        # =========================
        # 🟩 2. ĐI ĐẾN PHÒNG MỚI
        # =========================
        print(f"🚀 [1/3] Đến cửa phòng {room_num}...")
        if not self.navigate_to(target_room['door'], f"cửa phòng {room_num}"):
            return

        print(f"🚀 [2/3] Vào trong phòng {room_num}...")
        if not self.navigate_to(target_room['inside'], f"trong phòng {room_num}"):
            return

        print(f"🚀 [3/3] Đến trung tâm phòng {room_num}...")
        if self.navigate_to(target_room['center'], f"trung tâm phòng {room_num}"):
            self.current_room = room_num
            print(f"🏁 Hoàn thành! Robot đang ở phòng {room_num}.")


def main():
    rclpy.init()
    navigator = RoomNavigator()

    print('\n--- HỆ THỐNG ĐIỀU HƯỚNG ROBOT BỆNH VIỆN ---')

    while rclpy.ok():
        try:
            user_input = input("\nNhập số phòng (vd: 5) hoặc 'exit': ").strip()

            if user_input.lower() == 'exit':
                break

            if user_input:
                navigator.go_to_room(user_input)

        except KeyboardInterrupt:
            break

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()