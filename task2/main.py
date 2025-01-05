from state import State
import DataGenerator
import numpy as np
from render import VTKRender
import random
from enum import Enum
from pdf import ItemPDF
import time
from MCTS import MCTS, MCTS_strategy


if __name__ == "__main__":
    # 测试矩阵
    width = 100
    height = 100
    depth = 100

    block, _ = DataGenerator.generate_bpp_data_with_algorithm_1(num_items_range=(30,))

    block = np.array(block)
    print(block)

    begin_size = len(block)

    begin_time = time.time()
    mcts = MCTS(block, (width, height, depth), 1000, MCTS_strategy.avgDepth)
    list_ = mcts.main_procedure()

    render = VTKRender((width, height, depth))
    for action in list_:
        render.add_item(action[0], action[1])


    print("put", len(list_), "blocks")
    print("time:", time.time() - begin_time)
    render.hold_on()