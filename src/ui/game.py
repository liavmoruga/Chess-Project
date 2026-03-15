import pygame
import threading
import chess
from src.logic.board import Board
from src.ui.assets import AssetManager



# dimensions
WIDTH = 640
HEIGHT = 640
FPS = 60

# base colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND = (30, 30, 30)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)

# more colors
SELECTED_COLOR = (100, 109, 64)
HINT_COLOR = (100, 109, 64, 128)
SOURCE_COLOR = (206, 210, 107)
DEST_COLOR = (170, 162, 58)
CHECK_COLOR = (255, 0, 0)




# MAIN GAME

class ChessGame:
    def __init__(self, white_agent=None, black_agent=None):
        
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Chess Project - Liav Moruga")
        self.clock = pygame.time.Clock()
        
        self.assets = AssetManager()
        self.assets.load_content()
        
        self.board = Board()
        
        # agents
        self.white_agent = white_agent
        self.black_agent = black_agent
        
        # set agent colors
        if self.white_agent: self.white_agent.set_color(chess.WHITE)
        if self.black_agent: self.black_agent.set_color(chess.BLACK)
        
        # view settings
        self.flip_view = False
        # auto-flip if human plays black (white is bot, black is human)
        if self.white_agent is not None and self.black_agent is None:
            self.flip_view = True
        
        # state
        self.selected_square = None
        self.valid_moves = {}
        self.is_dragging = False
        self.drag_data = None
        self.clicked_selected = False
        
        # threading state
        self.agent_thinking = False
        self.agent_move_result = None
        self.agent_thread = None
        
        # layout
        self.sq_size = 0
        self.board_x = 0
        self.board_y = 0
        self.coord_font = None
        
        self._recalculate_layout(WIDTH, HEIGHT)

    def _recalculate_layout(self, w, h):
        min_dim = min(w, h)
        self.sq_size = min_dim // 8
        self.board_x = (w - (self.sq_size * 8)) // 2
        self.board_y = (h - (self.sq_size * 8)) // 2
        
        self.coord_font = pygame.font.SysFont('Arial', int(self.sq_size * 0.18), bold=True)
        
        # resize images
        self.assets.rescale_images(self.sq_size)

    def _deselect(self):
        self.selected_square = None
        self.valid_moves = {}
        self.is_dragging = False
        self.drag_data = None
        self.clicked_selected = False

    def _get_board_pos(self, mouse_pos):
        mx, my = mouse_pos[0] - self.board_x, mouse_pos[1] - self.board_y
        if self.sq_size > 0:
            row = my // self.sq_size
            col = mx // self.sq_size
            if self.flip_view:
                row = 7 - row
                col = 7 - col
            if 0 <= row < 8 and 0 <= col < 8:
                return (row, col)
        return None

    def _handle_click(self, pos):
        # checks
        if self.board.is_game_over(): return

        coords = self._get_board_pos(pos)
        if not coords:
            self._deselect()
            return

        # click on valid move
        if coords in self.valid_moves and not self.is_dragging:
            move_to_make = self.valid_moves[coords]
            self._execute_move(move_to_make)
            return

        # click on piece
        piece = self.board.get_piece_at(coords)
        if self.board.is_piece_turn(piece):
            if self.selected_square == coords:
                self.clicked_selected = True
            else:
                self.clicked_selected = False
            
            self.selected_square = coords
            self.valid_moves = self.board.get_valid_moves(coords)
            self.is_dragging = True
            self.drag_data = {'symbol': piece, 'pos': coords}
        else:
            self._deselect()

    def _handle_release(self):
        if not self.is_dragging:
            return

        mouse_pos = pygame.mouse.get_pos()
        coords = self._get_board_pos(mouse_pos)

        # released outside the board or on an invalid square
        if not coords:
            self._deselect()
            return

        # user released on a valid destination square
        if coords in self.valid_moves and coords != self.selected_square:
            self._execute_move(self.valid_moves[coords])
            return

        # user released on the same square they started on
        if coords == self.selected_square:
            if self.clicked_selected:
                self._deselect()
            else:
                self.is_dragging = False
                self.drag_data = None
            return

        self._deselect()

    def _execute_move(self, move):
        is_capture = self.board.move_piece(move)
        
        if self.board.is_checkmate():
            self.assets.play_sound('checkmate')
        elif is_capture:
            self.assets.play_sound('capture')
        else:
            self.assets.play_sound('move')
            
        self._deselect()

    def _run_agent_move(self, agent):
        # runs in separate thread
        move = agent.get_move(self.board)
        self.agent_move_result = move

    def run(self):
        running = True
        while running:
            # check turn
            is_white = self.board.is_turn
            current_agent = self.white_agent if is_white else self.black_agent
            
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False # Stop the loop instead of killing the program
                elif event.type == pygame.VIDEORESIZE:
                    self._recalculate_layout(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f: 
                        self.flip_view = not self.flip_view
                
                # human input
                # only allow if it's human turn (agent is None) and not waiting for thread
                if current_agent is None and not self.agent_thinking and not self.board.is_game_over():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self._handle_click(event.pos)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self._handle_release()

            # agent logic
            if current_agent is not None and not self.board.is_game_over():
                if not self.agent_thinking:
                    # start thinking
                    self.agent_thinking = True
                    self.agent_thread = threading.Thread(target=self._run_agent_move, args=(current_agent,))
                    self.agent_thread.start()
                
                # check if done
                if not self.agent_thread.is_alive():
                    if self.agent_move_result:
                        move = self.agent_move_result
                        self._execute_move(move)
                    self.agent_thinking = False
                    self.agent_move_result = None

            # draw
            self.screen.fill(BACKGROUND)
            self._draw_board()
            self._draw_hints()
            self._draw_pieces()
            
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def _draw_board(self):
        for r in range(8):
            for c in range(8):
                dr = 7 - r if self.flip_view else r
                dc = 7 - c if self.flip_view else c
                x = self.board_x + dc * self.sq_size
                y = self.board_y + dr * self.sq_size
                
                # tile colors
                color = LIGHT_BROWN if (r+c)%2==0 else DARK_BROWN
                
                # last move highlight
                if self.board.last_move:
                    move = self.board.last_move
                    sr = 7 - chess.square_rank(move.from_square)
                    sc = chess.square_file(move.from_square)
                    er = 7 - chess.square_rank(move.to_square)
                    ec = chess.square_file(move.to_square)
                    if (r, c) == (sr, sc): color = SOURCE_COLOR
                    elif (r, c) == (er, ec): color = DEST_COLOR
                
                # selection highlight
                if self.selected_square == (r,c): color = SELECTED_COLOR
                
                # check highlight
                if self.board.is_in_check():
                    king_pos = self.board.get_king_pos()
                    if king_pos == (r, c):
                        color = CHECK_COLOR

                pygame.draw.rect(self.screen, color, (x, y, self.sq_size, self.sq_size))
                
                # coordinates
                txt_color = DARK_BROWN if (r+c)%2==0 else LIGHT_BROWN
                pad = int(self.sq_size * 0.03)
                
                if dc == 7: 
                    lbl = self.coord_font.render(str(8-r), True, txt_color)
                    self.screen.blit(lbl, (x + self.sq_size - lbl.get_width() - pad, y + pad))
                if dr == 7: 
                    lbl = self.coord_font.render(chr(ord('a')+c), True, txt_color)
                    self.screen.blit(lbl, (x + pad, y + self.sq_size - lbl.get_height() - pad))

    def _draw_hints(self):
        for pos in self.valid_moves.keys():
            dr = 7 - pos[0] if self.flip_view else pos[0]
            dc = 7 - pos[1] if self.flip_view else pos[1]
            x = self.board_x + dc * self.sq_size
            y = self.board_y + dr * self.sq_size
            
            target = self.board.get_piece_at(pos)
            s = pygame.Surface((self.sq_size, self.sq_size), pygame.SRCALPHA)
            
            if not target:
                rad = int(self.sq_size * 0.125)
                pygame.draw.circle(s, HINT_COLOR, (self.sq_size//2, self.sq_size//2), rad)
            else:
                tl = int(self.sq_size * 0.2)
                w, h = self.sq_size, self.sq_size
                pygame.draw.polygon(s, HINT_COLOR, [(0,0), (tl,0), (0,tl)])
                pygame.draw.polygon(s, HINT_COLOR, [(w,0), (w-tl,0), (w,tl)])
                pygame.draw.polygon(s, HINT_COLOR, [(0,h), (0,h-tl), (tl,h)])
                pygame.draw.polygon(s, HINT_COLOR, [(w,h), (w-tl,h), (w,h-tl)])
            self.screen.blit(s, (x, y))

    def _draw_pieces(self):
        mx, my = pygame.mouse.get_pos()
        is_checkmate = self.board.is_checkmate()
        is_draw = self.board.is_draw() # Fetch draw status
        
        for r in range(8):
            for c in range(8):
                piece = self.board.get_piece_at((r, c))
                if piece:
                    if self.is_dragging and self.drag_data['pos'] == (r, c): continue
                    
                    dr = 7 - r if self.flip_view else r
                    dc = 7 - c if self.flip_view else c
                    x = self.board_x + dc * self.sq_size
                    y = self.board_y + dr * self.sq_size
                    
                    img = self.assets.get_image(piece)
                    
                    # Rotate current king if checkmate, OR rotate BOTH kings if draw
                    if (is_checkmate and piece.lower() == 'k' and self.board.is_piece_turn(piece)) or \
                       (is_draw and piece.lower() == 'k'):
                        img = pygame.transform.rotate(img, 90)
                        new_rect = img.get_rect(center=(x + self.sq_size//2, y + self.sq_size//2))
                        self.screen.blit(img, new_rect)
                    else:
                        if img: self.screen.blit(img, (x, y))

        if self.is_dragging and self.drag_data:
            piece = self.drag_data['symbol']
            img = self.assets.get_image(piece)
            if img:
                rect = img.get_rect(center=(mx, my))
                self.screen.blit(img, rect)

