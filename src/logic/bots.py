import chess
import random
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




class RandomBot(Agent):
    def __init__(self, wait_time):
        super().__init__()
        self.wait_time = wait_time

    def get_move(self, board_obj):
        legal_moves = list(board_obj.engine.legal_moves)
        
        if not legal_moves:
            return None 
            
        move = random.choice(legal_moves)
        
        sr = 7 - chess.square_rank(move.from_square)
        sc = chess.square_file(move.from_square)
        er = 7 - chess.square_rank(move.to_square)
        ec = chess.square_file(move.to_square)
        
        time.sleep(self.wait_time)
        return (sr, sc), (er, ec)