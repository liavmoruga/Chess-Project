import chess
import numpy as np

# BOARD LOGIC

class Board:
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        self.engine = chess.Board(fen)
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
                
                # temporary: make default promotion to queen
                if move.promotion is not None:
                    if move.promotion == chess.QUEEN:
                        moves[(tr, tc)] = move
                else:
                    moves[(tr, tc)] = move
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

    def is_white_turn(self):
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





    @staticmethod
    def engine_to_tensor(engine):
        """
        Translates a chess board into an 8x8x18 numerical tensor using int8.
        Channels 0-11: Pieces
        Channel 12: Turn (1 if White, 0 if Black)
        Channels 13-16: Castling rights
        Channel 17: En Passant target square
        """
        # Upgraded to 18 channels
        tensor = np.zeros((8, 8, 18), dtype=np.int8)
        piece_map = engine.piece_map()
        
        # 1. Piece placements
        for square, piece in piece_map.items():
            row = chess.square_rank(square)
            col = chess.square_file(square)
            piece_type = piece.piece_type - 1
            color_offset = 0 if piece.color == chess.WHITE else 6
            tensor[row, col, piece_type + color_offset] = 1
            
        # 2. Whose turn is it?
        if engine.turn == chess.WHITE:
            tensor[:, :, 12] = 1
            
        # 3. Castling rights
        if engine.has_kingside_castling_rights(chess.WHITE):
            tensor[:, :, 13] = 1
        if engine.has_queenside_castling_rights(chess.WHITE):
            tensor[:, :, 14] = 1
        if engine.has_kingside_castling_rights(chess.BLACK):
            tensor[:, :, 15] = 1
        if engine.has_queenside_castling_rights(chess.BLACK):
            tensor[:, :, 16] = 1
            
        # 4. En Passant target square
        if engine.ep_square is not None:
            row = chess.square_rank(engine.ep_square)
            col = chess.square_file(engine.ep_square)
            tensor[row, col, 17] = 1
            
        return tensor