import pandas as pd
import numpy as np

class Item:
    def __init__(self, length, width, height, qty):
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.qty = qty

class Container:
    def __init__(self, length, width, height):
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.total_volume = self.length * self.width * self.height
        self.used_volume = 0
        self.items = []
        self.space = np.zeros((int(self.length), int(self.width), int(self.height)), dtype=int)  # 初始化容器空间

    def can_fit(self, item, position, rotate=False):
        # 判断物品是否能放入容器，并考虑旋转
        item_dims = [float(item.length), float(item.width), float(item.height)]
        if rotate:
            for _ in range(6):
                if self._check_fit(item_dims, position):
                    return True
                item_dims = self._rotate_item(item_dims)
        else:
            return self._check_fit(item_dims, position)
        return False

    def _check_fit(self, item_dims, position):
        x, y, z = position
        x = int(x)
        y = int(y)
        z = int(z)
        if (x + item_dims[0] <= self.length and 
            y + item_dims[1] <= self.width and 
            z + item_dims[2] <= self.height):
            return self.space[x:x+int(item_dims[0]), y:y+int(item_dims[1]), z:z+int(item_dims[2])].sum() == 0
        return False

    def _rotate_item(self, dims):
        # 旋转物品，依次改变各维度的顺序
        return [dims[1], dims[2], dims[0]]

    def place(self, item, position, rotate=False):
        # 放置物品并更新容器空间
        item_dims = [float(item.length), float(item.width), float(item.height)]
        if rotate:
            item_dims = self._rotate_item(item_dims)
        x, y, z = position
        x = int(x)
        y = int(y)
        z = int(z)
        self.space[x:x+int(item_dims[0]), y:y+int(item_dims[1]), z:z+int(item_dims[2])] = 1
        self.items.append((item, position, rotate))
        self.used_volume += item_dims[0] * item_dims[1] * item_dims[2]

def read_orders(file_path):
    df = pd.read_csv(file_path)
    orders = {}
    for _, row in df.iterrows():
        order_id = row['sta_code']
        if order_id not in orders:
            orders[order_id] = []
        for _ in range(row['qty']):
            orders[order_id].append(Item(row['长(CM)'], row['宽(CM)'], row['高(CM)'], 1))
    return orders

def pack_order(items, container_sizes):
    packed_containers = []
    used_containers = set()  # 跟踪已经使用过的容器

    for item in items:
        placed = False
        # 尝试将物品放入已有的容器
        for container in packed_containers:
            for i in range(int(container.length)):
                for j in range(int(container.width)):
                    for k in range(int(container.height)):
                        if container.can_fit(item, (i, j, k), rotate=True):
                            container.place(item, (i, j, k), rotate=True)
                            placed = True
                            break
                    if placed: break
                if placed: break
            if placed: break

        # 如果当前容器无法放下物品，则尝试新的容器
        if not placed:
            for size in container_sizes:
                if size not in used_containers:  # 确保每种容器只能使用一次
                    new_container = Container(*size)
                    for i in range(int(new_container.length)):
                        for j in range(int(new_container.width)):
                            for k in range(int(new_container.height)):
                                if new_container.can_fit(item, (i, j, k), rotate=True):
                                    new_container.place(item, (i, j, k), rotate=True)
                                    packed_containers.append(new_container)
                                    used_containers.add(size)
                                    placed = True
                                    break
                            if placed: break
                        if placed: break
                    if placed: break
    return packed_containers

def write_order_to_file(order_id, containers, file_path='output.txt'):
    total_volume = sum(container.total_volume for container in containers)
    used_volume = sum(container.used_volume for container in containers)
    utilization = used_volume / total_volume
    remaining_items = sum(len(container.items) for container in containers)

    with open(file_path, 'a') as file:
        file.write(f"订单号: {order_id}")
        file.write(f"  容器组合: {[f'({c.length}, {c.width}, {c.height})' for c in containers]}")
        file.write(f"  总空间利用率: {utilization:.2f}\n")

# 主程序
if __name__ == "__main__":
    # 读取订单数据
    orders = read_orders('task3.csv')

    # 可用的容器尺寸
    container_sizes = [
        (35, 23, 13), (37, 26, 13), (38, 26, 13), (40, 28, 16), 
        (42, 30, 18), (42, 30, 40), (52, 40, 17), (54, 45, 36)
    ]

    # 对每个订单进行物品摆放
    for order_id, items in orders.items():
        # 按体积从大到小排序
        items.sort(key=lambda item: item.length * item.width * item.height, reverse=True)
        packed_containers = pack_order(items, container_sizes)
        # 将每个订单的结果写入文件
        write_order_to_file(order_id, packed_containers)
