import random
import chess
import time


# AGENT INTERFACE

class Agent:
    def __init__(self):
        self.color = None

    def set_color(self, color):
        self.color = color

    def get_move(self, board_obj):
        # return ((start_row, start_col), (end_row, end_col)) or None
        raise NotImplementedError
