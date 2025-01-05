import torch
import DataGenerator
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


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

        filled = self.board == 1

        colors = np.empty(self.board.shape, dtype=object)
        colors[self.board == 1] = 'blue'

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
        for tile in tiles:
            if tile[0] <= max_allowed_row_size and tile[1] <= max_allowed_col_size and tile[2] <= max_allowed_height_size:
                possible_moves.append(tile)
        return possible_moves

    def add_block_to_board(self, block, position):
        x, y, z = position
        l, w, h = block
        #print(f"Adding block to board: Position=({x}, {y}, {z}), Size=({l}, {w}, {h})")  # 调试信息
        self.board[int(x):int(x)+int(l), int(y):int(y)+int(w), int(z):int(z)+int(h)] = 1


    def is_valid_pos_for_block(self, block, position):
        x, y, z = position
        l, w, h = block
        if (x + l > self.board.shape[0] or y + w > self.board.shape[1] or z + h > self.board.shape[2]):
            return False

        placed_place = self.board[int(x):int(x)+int(l), int(y):int(y)+int(w), int(z):int(z)+int(h)]
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
    def find_largest_zero_block(arr):
        shape = arr.shape
        max_size = 0
        max_block = None
        dp_x = np.zeros_like(arr, dtype=int)
        dp_y = np.zeros_like(arr, dtype=int)
        dp_z = np.zeros_like(arr, dtype=int)
        for x in range(shape[0]):
            for y in range(shape[1]):
                for z in range(shape[2]):
                    if arr[x, y, z] == 0:
                        if x == 0:
                            dp_x[x, y, z] = 1
                        else:
                            dp_x[x, y, z] = dp_x[x-1, y, z] + 1
                        if y == 0:
                            dp_y[x, y, z] = 1
                        else:
                            dp_y[x, y, z] = dp_y[x, y-1, z] + 1
                        if z == 0:
                            dp_z[x, y, z] = 1
                        else:
                            dp_z[x, y, z] = dp_z[x, y, z-1] + 1
                        length = dp_x[x, y, z]
                        width = dp_y[x, y, z]
                        height = dp_z[x, y, z]
                        volume = length * width * height
                        if volume > max_size:
                            max_size = volume
                            max_block = (x - length + 1, y - width + 1, z - height + 1, length, width, height)
        return max_block, max_size

if __name__ == "__main__":
    pass
