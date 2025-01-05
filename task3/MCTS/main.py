from state import State
import DataGenerator
import numpy as np
import random
from enum import Enum
from pdf import ItemPDF
import time
from MCTS import MCTS, MCTS_strategy
import itertools
import pandas as pd

def select_best_containers(blocks, containers):
    best_combination = None
    best_utilization = 0
    best_total_volume = 0
    best_used_volume = 0

    total_block_volume = sum(np.prod(block) for block in blocks)  # 计算所有物品的总体积

    for i in range(1, len(containers) + 1):
        for combination in itertools.combinations(containers, i):
            total_volume = sum(np.prod(container) for container in combination)
            used_volume = 0

            remaining_blocks = np.copy(blocks)
            all_placed = True  # 标记所有物品是否都能放入

            for container in combination:
                mcts = MCTS(remaining_blocks, container, 5, MCTS_strategy.avgDepth)
                placed_blocks, _ = mcts.main_procedure()
                used_volume += sum(np.prod(block[0]) for block in placed_blocks)
                remaining_blocks = np.array([block for block in remaining_blocks if not any(np.array_equal(block, placed_block[0]) for placed_block in placed_blocks)])

            if used_volume == total_block_volume:  # 检查放入物品的总体积是否与实际总体积相等
                utilization = total_block_volume / total_volume  # 使用全部物品体积除以使用的容器总体积计算利用率
                if utilization > best_utilization:
                    best_utilization = utilization
                    best_combination = combination
                    best_total_volume = total_volume
                    best_used_volume = used_volume

    return best_combination, best_utilization, best_total_volume, best_used_volume, remaining_blocks

def write_order_result(order_id, best_containers, best_utilization, file_path='output.csv'):
    with open(file_path, 'a') as file:
        file.write(f"订单号: {order_id}, 容器组合: {best_containers}, 总空间利用率: {best_utilization:.2f}\n")

# 读取CSV文件并手动指定列名
test_data = pd.read_csv('task3.csv', sep=',', names=['sta_code', 'sku_code', '长(CM)', '宽(CM)', '高(CM)', 'qty'])

# 提取订单号并分组
order_groups = test_data.groupby('sta_code')

# 可用的容器尺寸
containers = [
    (35, 23, 13),
    (37, 26, 13),
    (38, 26, 13),
    (40, 28, 16),
    (42, 30, 18),
    (42, 30, 40),
    (52, 40, 17),
    (54, 45, 36)
]

# 对每个订单单独处理
for order_id, group in order_groups:
    blocks = []
    for _, row in group.iterrows():
        length = row['长(CM)']
        width = row['宽(CM)']
        height = row['高(CM)']
        qty = int(row['qty'])  # 将qty转换为整数
        for _ in range(qty):
            blocks.append((length, width, height))

    blocks = np.array(blocks)
    best_containers, best_utilization, best_total_volume, best_used_volume, remaining_blocks = select_best_containers(blocks, containers)
    print(f"订单号: {order_id}, 最佳容器组合: {best_containers}, 总空间利用率: {best_utilization:.2f}")  # 调试信息
    write_order_result(order_id, best_containers, best_utilization)

print("结果已保存到 output_results.csv 文件中。")
