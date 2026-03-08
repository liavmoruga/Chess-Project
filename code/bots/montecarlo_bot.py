import io
import chess
import chess.pgn
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from logic.agent import Agent

def fen_to_vector(fen):
    board = chess.Board(fen)
    vector = np.zeros(64, dtype=np.float32)
    # Basic piece values for numerical representation
    piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 10,
                    'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -10}
    
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            vector[i] = piece_values[piece.symbol()]
    return vector

# ==========================================
# 3. MONTECARLO BOT CLASS
# ==========================================
class MonteCarloBot(Agent):
    """
    A simple bot that uses the trained Neural Network to evaluate all legal moves 
    and picks the one that results in the highest score for White or lowest for Black.
    """
    def __init__(self, model_path="montecarlo_model.keras"):
        super().__init__()
        try:
            self.model = tf.keras.models.load_model(model_path)
            print(f"Successfully loaded model from {model_path}")
        except Exception as e:
            print(f"Error loading model (make sure to train it first!): {e}")
            self.model = None

    def get_move(self, board_obj):
        if self.model is None:
            print("Model is not loaded. Cannot make a move.")
            return None
            
        engine = board_obj.engine
        legal_moves = list(engine.legal_moves)
        
        if not legal_moves:
            return None

        # Predict the score for every possible next move
        X_batch = []
        moves_list = []

        for move in legal_moves:
            engine.push(move)
            X_batch.append(fen_to_vector(engine.fen()))
            engine.pop()
            moves_list.append(move)

        # Batch predict to be much faster than looping predict
        predictions = self.model.predict(np.array(X_batch), verbose=0)

        best_move = None
        # White wants the highest score (+1), Black wants the lowest score (-1)
        best_score = -float('inf') if self.color == chess.WHITE else float('inf')

        for i, pred in enumerate(predictions):
            score = pred[0]
            if self.color == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = moves_list[i]
            else:
                if score < best_score:
                    best_score = score
                    best_move = moves_list[i]

        if best_move:
            # Convert chess library move into your Board API's expected format: 
            # ((start_row, start_col), (end_row, end_col))
            sr = 7 - chess.square_rank(best_move.from_square)
            sc = chess.square_file(best_move.from_square)
            er = 7 - chess.square_rank(best_move.to_square)
            ec = chess.square_file(best_move.to_square)
            return ((sr, sc), (er, ec))

        return None
