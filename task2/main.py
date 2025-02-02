import DataGenerator
import numpy as np
from render import VTKRender
import time
from MCTS import MCTS, MCTS_strategy


if __name__ == "__main__":
    width = 100
    height = 100
    depth = 100

    block, _ = DataGenerator.generate_bpp_data_with_algorithm_1(num_items_range=(30,))

    block = np.array(block)
    print(block)

    begin_size = len(block)

    begin_time = time.time()
    mcts = MCTS(block, (width, height, depth), 10, MCTS_strategy.avgDepth)
    list_ = mcts.main_procedure()
    end_time = time.time()
    print("time:", end_time - begin_time, "s")

    render = VTKRender((width, height, depth))
    for action in list_:
        render.add_item(action[0], action[1])

    print("put", len(list_), "blocks")

    render.hold_on()
