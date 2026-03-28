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
    def __init__(self, func, depth, k=1, threshold=0.0):
        super().__init__()
        self.func = func
        self.depth = depth
        self.k = k
        self.threshold = threshold

    def get_move(self, board_obj):
        board = board_obj.engine.copy()
        
        # Dynamically get the color
        bot_color = board.turn 
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
            
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

        alpha = -float("inf")
        beta = float("inf")
        move_scores = []

        # Evaluate all root moves to find the Top-K
        for move in legal_moves:
            board.push(move)
            value = self.minimax(board, self.depth - 1, alpha, beta, not (bot_color == chess.WHITE))
            board.pop()
            
            move_scores.append((move, value))
            
            # Maintain standard alpha-beta pruning at the root
            if bot_color == chess.WHITE:
                alpha = max(alpha, value)
            else:
                beta = min(beta, value)

        # Sort moves: White wants highest scores, Black wants lowest scores
        if bot_color == chess.WHITE:
            move_scores.sort(key=lambda x: x[1], reverse=True)
        else:
            move_scores.sort(key=lambda x: x[1])

        best_score = move_scores[0][1]
        valid_moves = []

        # Filter moves that fall within the acceptable threshold
        for move, score in move_scores:
            # Explicitly catch exact matches first to bypass 'nan' math on infinities
            if score == best_score:
                valid_moves.append(move)
            elif abs(best_score - score) <= self.threshold:
                valid_moves.append(move)
            else:
                break # The list is sorted, so once we drop below threshold, we can stop

        # Take the Top-K from the filtered list and pick randomly
        top_k_moves = valid_moves[:self.k]
        return random.choice(top_k_moves)


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
    
    # 64-square map granting fractional points for controlling the center
    # Indexes match python-chess squares (0 = A1, 63 = H8)
    center_bonus = [
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0,
        0.0, 0.0, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0,
        0.0, 0.0, 0.1, 0.2, 0.2, 0.1, 0.0, 0.0,
        0.0, 0.0, 0.1, 0.1, 0.1, 0.1, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    ]

    score = 0
    for piece_type, value in piece_values.items():
        # Add value + center bonus for white pieces
        for square in engine.pieces(piece_type, chess.WHITE):
            score += value + center_bonus[square]
            
        # Subtract value + center bonus for black pieces
        for square in engine.pieces(piece_type, chess.BLACK):
            score -= (value + center_bonus[square])
            
    return score

class MaterialBot(MinimaxBot):
    # Pass k and threshold to the parent class
    def __init__(self, depth, k=1, threshold=0.0):
        super().__init__(evaluate_material, depth, k, threshold)


try:
    model = tf.keras.models.load_model('evaluator.keras')
except Exception as e:
    print("Warning: could not load evaluator.keras")
    model = None

def evaluate_model(engine):
    if model is None:
        return 0
        
    tensor = Board.engine_to_tensor(engine)
    score = model(np.expand_dims(tensor, axis=0), training=False)[0][0]
    return float(score)

class SmartBot(MinimaxBot):
    # Pass k and threshold to the parent class
    def __init__(self, depth, k=1, threshold=0.0):
        super().__init__(evaluate_model, depth, k, threshold)