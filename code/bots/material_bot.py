import chess
from code.logic.agent import Agent

class MaterialBot(Agent):
    def __init__(self, depth):
        super().__init__()
        self.depth = depth

    def evaluate(self, board):
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        
        score = 0
        # Fast evaluation using python-chess bitboards
        for piece_type, value in piece_values.items():
            # Add points for White's pieces
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            
            # Subtract points for Black's pieces
            score -= len(board.pieces(piece_type, chess.BLACK)) * value
            
        return score

    def get_move(self, board_obj):
        board = board_obj.engine.copy()
        
        best_move = None
        best_value = -99999 if self.color == chess.WHITE else 99999
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)

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

    def minimax(self, board, depth, alpha, beta, search_max):
        if depth <= 0:
            return self.evaluate(board)

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
                return -9999 if board.is_check() else 0
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
                return 9999 if board.is_check() else 0
            return min_value




