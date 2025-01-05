import random
import numpy as np

# def generate_bpp_data_with_algorithm_1(container_size=(100, 100, 100), num_items_range=(10, 50)):
#     """
#     根据 Algorithm 1 生成 Bin Packing Problem 数据。
#     """
#     items = [{"size": container_size, "position": (0, 0, 0), "rotation": (0, 0, 0)}]
#     num_items = random.randint(*num_items_range)

#     while len(items) < num_items:
#         # 从列表中随机选择一个物品
#         item_index = random.randint(0, len(items) - 1)
#         selected_item = items.pop(item_index)
#         axis = random.choice([0, 1, 2])  # 随机选择轴
#         item_size = selected_item["size"]
#         axis_length = item_size[axis]
#         split_position = random.randint(1, axis_length - 1)

#         # 分割生成两个新物品
#         new_item1_size = list(item_size)
#         new_item2_size = list(item_size)
#         new_item1_size[axis] = split_position
#         new_item2_size[axis] = axis_length - split_position

#         rotation1 = (random.choice([0, 90]), random.choice([0, 90]), random.choice([0, 90]))
#         rotation2 = (random.choice([0, 90]), random.choice([0, 90]), random.choice([0, 90]))

#         position1 = selected_item["position"]
#         position2 = list(selected_item["position"])
#         position2[axis] += split_position

#         new_item1 = {"size": tuple(new_item1_size), "position": tuple(position1), "rotation": rotation1}
#         new_item2 = {"size": tuple(new_item2_size), "position": tuple(position2), "rotation": rotation2}
#         items.append(new_item1)
#         items.append(new_item2)

#     # 转换为训练格式
#     item_sizes = [item["size"] for item in items]
#     labels = [(item["position"], item["rotation"]) for item in items]

#     return item_sizes, labels

import random

def generate_bpp_data_with_algorithm_1(container_size=(100, 100, 100), num_items_range=(10, 50)):
    items = [{"size": container_size, "position": (0, 0, 0), "rotation": (0, 0, 0)}]
    num_items = 0
    if len(num_items_range) == 1:
        num_items = num_items_range[0]
    else:
        num_items = random.randint(*num_items_range)

    while len(items) < num_items:
        item_index = random.randint(0, len(items) - 1)
        selected_item = items.pop(item_index)
        
        # 获取物品的大小
        item_size = selected_item["size"]
        
        # 计算每个轴的长度，并以长度作为权重
        axis_lengths = item_size
        total_length = sum(axis_lengths)
        
        # 选择轴的概率与长度成正比
        axis = random.choices([0, 1, 2], weights=axis_lengths, k=1)[0]
        
        axis_length = item_size[axis]
        if axis_length <= 2:
            continue
        split_position = random.randint(1, axis_length - 1)

        # 分割生成两个新物品
        new_item1_size = list(item_size)
        new_item2_size = list(item_size)
        new_item1_size[axis] = split_position
        new_item2_size[axis] = axis_length - split_position

        rotation1 = (random.choice([0, 90]), random.choice([0, 90]), random.choice([0, 90]))
        rotation2 = (random.choice([0, 90]), random.choice([0, 90]), random.choice([0, 90]))

        position1 = selected_item["position"]
        position2 = list(selected_item["position"])
        position2[axis] += split_position

        new_item1 = {"size": tuple(new_item1_size), "position": tuple(position1), "rotation": rotation1}
        new_item2 = {"size": tuple(new_item2_size), "position": tuple(position2), "rotation": rotation2}
        items.append(new_item1)
        items.append(new_item2)

    item_sizes = [item["size"] for item in items]
    labels = [(item["position"], item["rotation"]) for item in items]

    return item_sizes, labels



if __name__ == "__main__":
    item_sizes, labels = generate_bpp_data_with_algorithm_1()
    print(item_sizes)
    print(labels)

