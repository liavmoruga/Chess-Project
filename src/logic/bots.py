import random
from src.logic.agent import Agent


class RandomBot(Agent):
    def __init__(self):
        super().__init__()

    def get_move(self, board_obj):
        legal_moves = list(board_obj.engine.legal_moves)
        
        if not legal_moves:
            return None 
            
        move = random.choice(legal_moves)
        
        return move
