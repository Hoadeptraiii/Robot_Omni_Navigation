import yaml
import numpy as np
import matplotlib.pyplot as plt
import random
import time

# ============================================================
# PHẦN 1: ĐỌC DỮ LIỆU PHÒNG TỪ YAML
# ============================================================

def load_room_data(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data['rooms']

def get_door_coordinates(room_data, selected_rooms):
    points = []
    valid_rooms = []
    for room_name in selected_rooms:
        if room_name in room_data:
            door = room_data[room_name]['door']
            points.append([door['x'], door['y']])
            valid_rooms.append(room_name)
        else:
            print(f"[Cảnh báo] Không tìm thấy phòng: {room_name}")
    return np.array(points), valid_rooms


# ============================================================
# PHẦN 2: GENETIC ALGORITHM - TÌM ĐƯỜNG ĐI NGẮN NHẤT
# ============================================================

def distance(points, a, b):
    return np.linalg.norm(points[a] - points[b])

def total_cost(route, points):
    n = len(route)
    return sum(distance(points, route[i], route[(i + 1) % n]) for i in range(n))

def random_route(n):
    route = list(range(n))
    random.shuffle(route)
    return route

def crossover(parent1, parent2, n):
    a, b = sorted(random.sample(range(n), 2))
    child = [-1] * n
    child[a:b] = parent1[a:b]
    fill = [gene for gene in parent2 if gene not in child]
    idx = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = fill[idx]
            idx += 1
    return child

def mutate(route):
    route = route.copy()
    i, j = random.sample(range(len(route)), 2)
    route[i], route[j] = route[j], route[i]
    return route

def run_ga(points, population_size=50, num_generations=100):
    n = len(points)

    # Với <= 3 điểm, GA không cần thiết — trả về brute-force luôn
    if n <= 3:
        from itertools import permutations
        best_cost = float('inf')
        best_route = None
        for perm in permutations(range(n)):
            perm = list(perm)
            c = total_cost(perm, points)
            if c < best_cost:
                best_cost = c
                best_route = perm
        print(f"[Brute-force] Tổng chi phí tốt nhất: {best_cost:.4f}")
        return best_route, best_cost, []

    # GA cho số phòng lớn hơn
    population = [random_route(n) for _ in range(population_size)]
    best_costs = []
    start_time = time.time()

    for gen in range(num_generations):
        population.sort(key=lambda r: total_cost(r, points))
        costs = [total_cost(r, points) for r in population]
        best_costs.append(costs[0])
        print(f"  Thế hệ {gen + 1:3d}: Chi phí tốt nhất = {best_costs[-1]:.4f}")

        new_pop = population[:10]                        # Giữ 10 cá thể tốt nhất (elitism)

        for _ in range(32):                              # 32 con từ crossover
            p1, p2 = random.sample(population[:25], 2)
            new_pop.append(crossover(p1, p2, n))

        for _ in range(14):                              # 14 con từ mutation
            p = random.choice(population[:20])
            new_pop.append(mutate(p))

        for _ in range(4):                               # 4 cá thể ngẫu nhiên mới
            new_pop.append(random_route(n))

        population = new_pop

    elapsed = time.time() - start_time
    best_route = min(population, key=lambda r: total_cost(r, points))
    best_cost = total_cost(best_route, points)

    print(f"\n[GA] Tổng chi phí tốt nhất: {best_cost:.4f}")
    print(f"[GA] Thời gian chạy: {elapsed:.4f} giây")
    return best_route, best_cost, best_costs


# ============================================================
# PHẦN 3: HIỂN THỊ KẾT QUẢ
# ============================================================

def plot_route(points, route, room_names, best_cost):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Sơ đồ lộ trình ---
    ax = axes[0]
    ordered = [points[i] for i in route] + [points[route[0]]]  # Quay về điểm đầu
    xs = [p[0] for p in ordered]
    ys = [p[1] for p in ordered]

    ax.plot(xs, ys, '-o', color='steelblue', linewidth=2, markersize=8, label="Lộ trình")
    ax.scatter(points[route[0]][0], points[route[0]][1], c='red', s=120, zorder=5, label="Điểm bắt đầu")

    for i, idx in enumerate(route):
        ax.annotate(
            f"{room_names[idx]}\n({i+1})",
            points[idx],
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=8,
            color='darkgreen'
        )

    ax.set_title(f"Lộ trình tối ưu\nTổng khoảng cách: {best_cost:.4f}", fontsize=12)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    ax.grid(True)

    # --- In thứ tự thăm phòng ---
    axes[1].axis('off')
    order_text = "Thứ tự thăm phòng:\n\n"
    for step, idx in enumerate(route):
        order_text += f"  Bước {step + 1}: {room_names[idx]}  →  ({points[idx][0]:.2f}, {points[idx][1]:.2f})\n"
    order_text += f"  (Quay ve {room_names[route[0]]})\n"
    order_text += f"\nTong khoang cach: {best_cost:.4f}"
    axes[1].text(0.1, 0.5, order_text, transform=axes[1].transAxes,
                 fontsize=11, verticalalignment='center', fontfamily='monospace',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    axes[1].set_title("Chi tiết lộ trình", fontsize=12)

    plt.tight_layout()
    plt.show()


def plot_ga_progress(best_costs):
    if not best_costs:
        return
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(best_costs) + 1), best_costs, marker='o', color='darkorange')
    plt.title("GA - Chi phí tốt nhất qua từng thế hệ")
    plt.xlabel("Thế hệ")
    plt.ylabel("Chi phí")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ============================================================
# PHẦN 4: CHƯƠNG TRÌNH CHÍNH
# ============================================================

if __name__ == "__main__":

    # --- Cấu hình ---
    YAML_PATH = "/home/thehoa/hospital_robot_nav/src/nav2_simple_navigation/config/rooms.yaml"

    # Chọn bất kỳ phòng nào bạn muốn robot đi qua
    selected_rooms = ['room_7', 'room_2', 'room_11']   # ← Thay đổi tại đây

    # --- Đọc dữ liệu ---
    print("=" * 50)
    print("Đọc dữ liệu phòng từ YAML...")
    all_rooms_info = load_room_data(YAML_PATH)
    points, valid_rooms = get_door_coordinates(all_rooms_info, selected_rooms)

    print(f"\nCác phòng hợp lệ: {valid_rooms}")
    print("Tọa độ cửa (door):")
    for name, coord in zip(valid_rooms, points):
        print(f"  {name}: x={coord[0]:.4f}, y={coord[1]:.4f}")

    # --- Chạy GA ---
    print(f"\n{'='*50}")
    print(f"Chạy Genetic Algorithm cho {len(valid_rooms)} phòng...")
    best_route, best_cost, best_costs = run_ga(
        points,
        population_size=50,
        num_generations=100        # Giảm xuống nếu chạy chậm
    )

    # --- In kết quả ---
    print(f"\n{'='*50}")
    print("KẾT QUẢ:")
    print(f"  Thứ tự thăm phòng: {[valid_rooms[i] for i in best_route]}")
    print(f"  Tổng khoảng cách:  {best_cost:.4f}")

    # --- Vẽ đồ thị ---
    plot_route(points, best_route, valid_rooms, best_cost)
    plot_ga_progress(best_costs)