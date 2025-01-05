from state import State
import DataGenerator
import numpy as np
from render import VTKRender
import random
from enum import Enum
from tqdm import tqdm
from pdf import ItemPDF
from time import sleep


class MCTS_strategy(Enum):
    avgDepth = 0
    maxDepth = 1


class MCTS:
    def __init__(self, block: np.ndarray, size=(100, 100, 100), nRoll=100, strategy=MCTS_strategy.avgDepth):
        self.state = State(np.zeros(size, dtype=np.bool_))
        self.block = block
        self.nRoll = nRoll
        self.strategy = strategy


    def performSimulation(self, state: State, block: np.ndarray):
        sim_state = State(state.board)
        sim_block = np.copy(block)
        depth = 0
        total_size = 0
        while sim_state.get_valid_next_moves(sim_block) is not None:
            lfb = sim_state.find_next_lfb()
            legal_move = sim_state.get_valid_next_moves(sim_block)
            if len(legal_move) == 0:
                break
            else:
                move_weight = []
                for move in legal_move:
                    move_weight.append(ItemPDF(move).compute_weight())
                
                
                next_tile_rand_index = random.choices(range(len(legal_move)), weights=move_weight)[0]
                move = legal_move[next_tile_rand_index]
                if sim_state.is_valid_pos_for_block(move, lfb):
                    sim_state.add_block_to_board(move, lfb)
                    sim_block = np.delete(sim_block, next_tile_rand_index, axis=0)
                    total_size += np.prod(move)
                else:
                    break
            depth += 1 
        return total_size
    

    @staticmethod
    def test_perform_simulation(state: State, block: np.ndarray):
        sim_state = State(state.board)
        sim_block = np.copy(block)
        total_size = 0
        actions = []
        while sim_state.get_valid_next_moves(sim_block) is not None:
            lfb = sim_state.find_next_lfb()
            legal_move = sim_state.get_valid_next_moves(sim_block)
            if len(legal_move) == 0:
                break
            else:
                move_weight = []
                for move in legal_move:
                    move_weight.append(ItemPDF(move).compute_weight())
                
                
                next_tile_rand_index = random.choices(range(len(legal_move)), weights=move_weight)[0]
                move = legal_move[next_tile_rand_index]
                if sim_state.is_valid_pos_for_block(move, lfb):
                    sim_state.add_block_to_board(move, lfb)
                    sim_block = np.delete(sim_block, next_tile_rand_index, axis=0)
                    total_size += np.prod(move)
                    actions.append([lfb, move])
                else:
                    break
        return total_size, actions
    
    @staticmethod
    def apply_action(state: State, action: np.ndarray, block: np.ndarray):
        state.add_block_to_board(action, state.find_next_lfb())
        block = np.delete(block, np.where((block == action).all(axis=1))[0][0], axis=0)


    def main_procedure(self):
        self.state.clear_board()
        legal_actions = self.state.get_valid_next_moves(self.block)
        action_list = []
        total_size = 0
        while len(legal_actions) > 0:
            best_action = [self.state.find_next_lfb(), legal_actions[0]]
            best_max_depth = 0
            best_avg_depth = 0
            for action in legal_actions:
                act_blocks = np.copy(self.block)
                act_state = State(self.state.board)
                state_lfb = act_state.find_next_lfb()
                act_state.add_block_to_board(action, state_lfb)
                act_blocks = np.delete(act_blocks, np.where((act_blocks == action).all(axis=1))[0][0], axis=0)
                depths = []
                for _ in range(self.nRoll):
                    depths.append(self.performSimulation(act_state, act_blocks))
                avg_depth = sum(depths) / len(depths) + np.prod(action)
                max_depth = max(depths) + np.prod(action)
                if self.strategy == MCTS_strategy.avgDepth:
                    if avg_depth > best_avg_depth:
                        best_avg_depth = avg_depth
                        best_action = action
                        print("expect size:", best_avg_depth + total_size)
                elif self.strategy == MCTS_strategy.maxDepth:
                    if max_depth > best_max_depth:
                        best_max_depth = max_depth
                        best_action = action
            if best_action is None:
                continue
            # MCTS.apply_action(self.state, best_action, self.block)
            this_lfb = self.state.find_next_lfb()
            self.state.add_block_to_board(best_action, this_lfb)
            self.block = np.delete(self.block, np.where((self.block == best_action).all(axis=1))[0][0], axis=0)
            action_list.append([best_action, this_lfb])
            total_size += np.prod(best_action)
            size_percent = total_size / np.prod(self.state.board.shape)
            print("size:", total_size, "percent:", size_percent)
            legal_actions = self.state.get_legal_Actions(self.block)
            print(len(legal_actions))
        
        
        # return action_list

        return action_list

        # for future use
        small_mstc = MCTS(self.block, remain_zero_block[3:], self.nRoll, self.strategy)



        small_action_list = small_mstc.main_procedure()
        
        if len(small_action_list) == 0:
            return action_list

        for action in small_action_list:
            action_list.append([action[0], action[1] + remain_zero_block[:3]])

        
        return action_list

            


if __name__ == "__main__":
    # 测试矩阵
    width = 100
    height = 100
    depth = 100

    block, _ = DataGenerator.generate_bpp_data_with_algorithm_1(num_items_range=(50,))

    block = np.array(block)
    print(block)

    begin_size = len(block)


    mcts = MCTS(block, (width, height, depth), 10, MCTS_strategy.avgDepth)
    list_ = mcts.main_procedure()

    render = VTKRender((width, height, depth))
    for action in list_:
        render.add_item(action[0], action[1])


    print("put", len(list_), "blocks")
    render.hold_on()


