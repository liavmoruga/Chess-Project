import chess
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from logic.agent import Agent

class MaterialBot(Agent):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }

    def get_move(self, board_obj):
        board = board_obj.engine.copy()
        
        best_move = None
        best_value = -99999 if self.color == chess.WHITE else 99999
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        alpha = -99999
        beta = 99999

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
        
        if best_move:
            sr = 7 - chess.square_rank(best_move.from_square)
            sc = chess.square_file(best_move.from_square)
            er = 7 - chess.square_rank(best_move.to_square)
            ec = chess.square_file(best_move.to_square)
            return (sr, sc), (er, ec)
            
        return None

    def evaluate_board(self, board):
        # fast evaluation using bitboards instead of looping 64 squares
        score = 0
        for piece_type, value in self.piece_values.items():
            if piece_type == chess.KING:
                continue
            
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
            
        return score

    def minimax(self, board, depth, alpha, beta, search_max):
        if depth <= 0:
            return self.evaluate_board(board)

        has_moves = False

        if search_max:
            max_value = -99999
            for move in board.legal_moves:
                has_moves = True
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_value = max(max_value, value)
                alpha = max(alpha, value)
                
                if beta <= alpha:
                    break
            
            if not has_moves:
                return -9999 if board.is_check() else 0
            return max_value
            
        else:
            min_value = 99999
            for move in board.legal_moves:
                has_moves = True
                board.push(move)
                value = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_value = min(min_value, value)
                beta = min(beta, value)
                
                if beta <= alpha:
                    break
            
            if not has_moves:
                return 9999 if board.is_check() else 0
            return min_value