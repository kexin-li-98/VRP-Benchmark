import time
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

print("🚀 开始使用 OR-Tools（CPU）计算路线...")
# 5个点位：0仓库，1/2/3/4客户
locations = np.array([
    [0, 0], [10, 10], [20, 20], [10, 20], [20, 10]
], dtype=np.float32)

# 生成欧式距离矩阵
n = locations.shape[0]
distance_matrix = np.zeros((n, n), dtype=int)
for i in range(n):
    for j in range(n):
        dx = locations[i,0] - locations[j,0]
        dy = locations[i,1] - locations[j,1]
        dist = np.sqrt(dx*dx + dy*dy)
        distance_matrix[i,j] = int(round(dist))

def create_data_model():
    data = {}
    data["distance_matrix"] = distance_matrix
    data["num_vehicles"] = 1
    data["depot"] = 0
    return data

data = create_data_model()
manager = pywrapcp.RoutingIndexManager(len(data["distance_matrix"]), data["num_vehicles"], data["depot"])
routing = pywrapcp.RoutingModel(manager)

def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data["distance_matrix"][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

start_time = time.time()
solution = routing.SolveWithParameters(search_parameters)
end_time = time.time()

if solution:
    route = []
    index = routing.Start(0)
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    route.append(manager.IndexToNode(index))
    total_cost = solution.ObjectiveValue()
    print("\n🎉 求解完成！")
    print(f"✅ 耗时: {end_time - start_time:.5f} s")
    print(f"✅ 最优路线: {route}")
    print(f"✅ 总距离: {total_cost}")
else:
    print("❌ 求解失败")