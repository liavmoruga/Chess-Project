import chess
import chess.pgn

# BOARD LOGIC

class Board:
    def __init__(self):
        self.engine = chess.Board()
        self.last_move = None

    def get_piece_at(self, pos):
        # convert (row, col) to chess square index
        # row 0 is rank 8, row 7 is rank 1
        square = chess.square(pos[1], 7 - pos[0])
        piece = self.engine.piece_at(square)
        return piece.symbol() if piece else None

    def get_valid_moves(self, start_pos):
        r, c = start_pos
        start_sq = chess.square(c, 7 - r)
        
        moves = {}
        for move in self.engine.legal_moves:
            if move.from_square == start_sq:
                tr = 7 - chess.square_rank(move.to_square)
                tc = chess.square_file(move.to_square)
                moves[(tr, tc)] = move # Map the destination grid coord directly to the move object
        return moves

    def move_piece(self, move):
        if move in self.engine.legal_moves:
            is_capture = self.engine.is_capture(move)
            self.engine.push(move)
            
            self.last_move = move

            return is_capture
        return False

    def is_piece_turn(self, piece_symbol):
        # checks if a specific piece belongs to the active player
        if not piece_symbol: return False
        is_white_piece = piece_symbol.isupper()
        return is_white_piece == self.engine.turn

    @property
    def is_turn(self):
        # returns true if it is white's turn, false if black
        return self.engine.turn

    def is_game_over(self):
        return self.engine.is_game_over()

    def is_in_check(self):
        return self.engine.is_check()

    def is_checkmate(self):
        return self.engine.is_checkmate()
    
    def is_draw(self):
        return self.engine.is_game_over() and not self.engine.is_checkmate()

    def get_king_pos(self):
        # find king of current turn
        king_sq = self.engine.king(self.engine.turn)
        if king_sq is not None:
            return (7 - chess.square_rank(king_sq), chess.square_file(king_sq))
        return None
