import time
import numpy as np

# --------------------------
# cuOpt VRP GPU Benchmark
# 目标：和 OR-Tools CPU baseline 对比
# --------------------------
try:
    from cuopt import routing
    CUOPT_AVAILABLE = True
except Exception as e:
    CUOPT_AVAILABLE = False
    print(f"⚠️ cuOpt 导入失败: {e}")
    print("当前环境缺少cuOpt依赖，这是本项目重点调研的兼容性问题")

if not CUOPT_AVAILABLE:
    exit()

# 点位：0=仓库，1~4客户，和CPU基线完全一致（保证公平对比）
locations = np.array([
    [0, 0], [10, 10], [20, 20], [10, 20], [20, 10]
], dtype=np.float32)

n_points = locations.shape[0]
# 距离矩阵
distance_matrix = np.zeros((n_points, n_points), dtype=np.float32)
for i in range(n_points):
    for j in range(n_points):
        dx = locations[i,0] - locations[j,0]
        dy = locations[i,1] - locations[j,1]
        distance_matrix[i,j] = np.sqrt(dx*dx + dy*dy)

# 构建cuOpt模型
data_model = routing.DataModel(n_locations=n_points, n_vehicles=2)
data_model.add_cost_matrix(distance_matrix)

solver_settings = routing.SolverSettings()
solver_settings.time_limit = 0.1

start_time = time.perf_counter()
solver = routing.Solver(data_model, solver_settings)
solution = solver.solve()
end_time = time.perf_counter()

if solution.is_solution_found:
    print("✅ GPU cuOpt 求解成功！")
    print(f"求解耗时：{end_time - start_time:.6f} s")
    print(f"总路径代价：{solution.objective_value:.2f}")
    print("路线：", solution.route)
else:
    print("❌ cuOpt 未找到可行解")
