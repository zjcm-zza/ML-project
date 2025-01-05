import torch
import DataGenerator
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from render import VTKRender


class State:
    def __init__(self, board):
        self.board = np.copy(board)

    
    def find_next_lfb(self):
        lfb = None
        index = np.unravel_index(np.argmax(self.board == 0), self.board.shape)
        if self.board[index] == 0:
            lfb = index
            return lfb
        else:
            return None
        

    def find_next_occupied_column(self, start_position):
        that_position_row_until_next_occupied = self.board[
            start_position[0], start_position[1]:, start_position[2]:
        ]
        col_index = np.unravel_index(np.argmax(that_position_row_until_next_occupied == 1), that_position_row_until_next_occupied.shape)


        trans_position = that_position_row_until_next_occupied.T
        height_index = np.unravel_index(np.argmax(trans_position == 1), trans_position.shape)

        return (start_position[0], start_position[1] + col_index[0], start_position[2] + height_index[0])
        

    def get_occupied_col_and_height(self, position):
        that_position_row_until_next_occupied = self.board[
            position[0], position[1]:, position[2]:
        ]
        col_and_height_nonzero = np.nonzero(that_position_row_until_next_occupied)
        occupied_col = None
        occupied_height = None
        if len(col_and_height_nonzero[0]) > 0:
            occupied_col = position[1] + col_and_height_nonzero[0][0]
        else:
            occupied_col = self.board.shape[1]
        if len(col_and_height_nonzero[1]) > 0:
            occupied_height = position[2] + col_and_height_nonzero[1][0]
        else:
            occupied_height = self.board.shape[2]
        return occupied_col, occupied_height
        

    def plot_3d_board(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Create a boolean array where True represents the presence of a voxel
        filled = self.board == 1

        # Define colors for the voxels
        colors = np.empty(self.board.shape, dtype=object)
        colors[self.board == 1] = 'blue'

        # Plot voxels
        ax.voxels(filled, facecolors=colors, edgecolor='k')

        plt.show()


    def get_valid_next_moves(self, tiles):
        possible_moves = []
        next_lfb = self.find_next_lfb()
        if next_lfb is None:
            return possible_moves

        next_occupied_cols, next_occupied_heights = self.get_occupied_col_and_height(next_lfb)
        max_allowed_row_size = self.board.shape[0] - next_lfb[0]
        max_allowed_col_size = next_occupied_cols - next_lfb[1]
        max_allowed_height_size = next_occupied_heights - next_lfb[2]

        for i, tile in enumerate(tiles):  # 使用 enumerate 方便修改 tiles
            # 定义所有旋转方式
            rotations = [
                tile,
                (tile[0], tile[2], tile[1]),
                (tile[1], tile[0], tile[2]),
                (tile[2], tile[0], tile[1]),
                (tile[1], tile[2], tile[0]),
                (tile[2], tile[1], tile[0]),
            ]
            for rotated_tile in rotations:
                if (
                    rotated_tile[0] <= max_allowed_row_size and
                    rotated_tile[1] <= max_allowed_col_size and
                    rotated_tile[2] <= max_allowed_height_size
                ):
                    possible_moves.append(rotated_tile)
                    tiles[i] = rotated_tile  # 修改原 tiles 数组中的 tile
                    break  # 找到满足条件的旋转方式后退出循环
        return possible_moves


        
    def add_block_to_board(self, block, position): # won't check if the position is valid
        self.board[position[0]:position[0]+block[0], position[1]:position[1]+block[1], position[2]:position[2]+block[2]] = 1


    def is_valid_pos_for_block(self, block, position):
        if (position + block > self.board.shape).any():
            return False
            
        placed_place = self.board[position[0]:position[0]+block[0], position[1]:position[1]+block[1], position[2]:position[2]+block[2]]
        if np.sum(placed_place) == 0:
            return True
        else:
            return False
        

    def get_legal_Actions(self, tiles):
        moves = self.get_valid_next_moves(tiles)
        legal_actions = []
        lfb = self.find_next_lfb()
        for move in moves:
            if self.is_valid_pos_for_block(move, lfb):
                legal_actions.append(move)
        return legal_actions


    def clear_board(self):
        if self.board.any():
            self.board = np.zeros(self.board.shape, dtype=np.bool_)


    @staticmethod
    def find_large_zero_block(arr, volume_threshold=100000):
        shape = arr.shape
        dp_x = np.zeros_like(arr)
        dp_y = np.zeros_like(arr)
        dp_z = np.zeros_like(arr)
        
        for x in range(shape[0]):
            for y in range(shape[1]):
                for z in range(shape[2]):
                    if arr[x, y, z] == 0:
                        # 计算三个方向的连续0长度
                        dp_x[x,y,z] = dp_x[x-1,y,z] + 1 if x > 0 else 1
                        dp_y[x,y,z] = dp_y[x,y-1,z] + 1 if y > 0 else 1
                        dp_z[x,y,z] = dp_z[x,y,z-1] + 1 if z > 0 else 1
                        
                        # 从最大可能的尺寸开始尝试
                        length = min(dp_x[x,y,z], shape[0])
                        width = min(dp_y[x,y,z], shape[1])
                        height = min(dp_z[x,y,z], shape[2])
                        
                        # 快速检查是否存在全0块
                        valid = True
                        # 只检查边界点和几个采样点
                        check_points = [
                            (x, y, z),  # 右上后角
                            (x-length+1, y-width+1, z-height+1),  # 左下前角
                            (x-length+1, y, z),  # 左上后角
                            (x, y-width+1, z),  # 右下后角
                            (x, y, z-height+1),  # 右上前角
                        ]
                        
                        for px, py, pz in check_points:
                            if not (0 <= px < shape[0] and 0 <= py < shape[1] and 0 <= pz < shape[2]) or arr[px,py,pz] != 0:
                                valid = False
                                break
                        
                        if valid:
                            volume = length * width * height
                            if volume >= volume_threshold:
                                return (x-length+1, y-width+1, z-height+1, length, width, height), volume

        return None, 0


if __name__ == "__main__":
    pass

