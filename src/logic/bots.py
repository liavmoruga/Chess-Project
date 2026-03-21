import random
from src.logic.agent import Agent
import chess
from src.logic.board import Board
import numpy as np
import tensorflow as tf

class RandomBot(Agent):
    def __init__(self):
        super().__init__()

    def get_move(self, board_obj):
        legal_moves = list(board_obj.engine.legal_moves)
        
        if not legal_moves:
            return None 
            
        move = random.choice(legal_moves)
        
        return move










class MinimaxBot(Agent):
    def __init__(self, func, depth):
        super().__init__()
        self.func = func
        self.depth = depth

    def get_move(self, board_obj):
        board = board_obj.engine.copy()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

        best_move = legal_moves[0]
        best_value = -float("inf") if self.color == chess.WHITE else float("inf")

        alpha = -float("inf")
        beta = float("inf")

        for move in legal_moves:
            board.push(move)
            value = self.minimax(board, self.depth - 1, alpha, beta, not (self.color == chess.WHITE))
            board.pop()
            
            if self.color == chess.WHITE:
                if value > best_value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)
            else:
                if value < best_value:
                    best_value = value
                    best_move = move
                beta = min(beta, best_value)
        
        return best_move


    def minimax(self, board, depth, alpha, beta, search_max):
        if depth <= 0:
            return self.func(board)

        has_moves = False
        
        legal_moves = list(board.legal_moves)
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

        if search_max:
            max_value = -99999
            for move in legal_moves:
                has_moves = True
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break
            
            if not has_moves:
                return -float("inf") if board.is_check() else 0
            return max_value
            
        else:
            min_value = 99999
            for move in legal_moves:
                has_moves = True
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_value = min(min_value, value)
                beta = min(beta, value)
                
                if beta <= alpha:
                    break
            
            if not has_moves:
                return float("inf") if board.is_check() else 0
            return min_value
















def evaluate_material(engine):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    score = 0
    for piece_type, value in piece_values.items():
        score += len(engine.pieces(piece_type, chess.WHITE)) * value
        score -= len(engine.pieces(piece_type, chess.BLACK)) * value
    return score

class MaterialBot(MinimaxBot):
    def __init__(self, depth):
        super().__init__(evaluate_material, depth)
























try:
    model = tf.keras.models.load_model('evaluator.keras')
except Exception as e:
    print("Warning: could not load evaluator.keras")
    model_model = None

def evaluate_model(engine):
    if model is None:
        return 0
        
    tensor = Board.engine_to_tensor(engine)
    score = model(np.expand_dims(tensor, axis=0), training=False)[0][0]
    return float(score)

class SmartBot(MinimaxBot):
    def __init__(self, depth):
        super().__init__(evaluate_model, depth)
