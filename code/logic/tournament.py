import time
import concurrent.futures
import multiprocessing
import chess
from logic.board import Board

def play_game(bot1, bot2, bot1_white, record_moves=False):
    board = Board()

    white_bot = bot1 if bot1_white else bot2
    black_bot = bot2 if bot1_white else bot1
    
    white_bot.set_color(chess.WHITE)
    black_bot.set_color(chess.BLACK)
    
    game_fens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"] if record_moves else []
    
    while not board.is_game_over():
        if board.is_turn:
            move = white_bot.get_move(board)
        else:
            move = black_bot.get_move(board)

        if move is None:
            break
        
        board.move_piece(move[0], move[1])
        if record_moves:
            game_fens.append(board.engine.fen())
    
    # in the chess library: 1-0 = white wins, 0-1 = black wins, 1/2-1/2 = draw
    result = board.engine.result()
    
    if result == '1-0':
        return (1.0, 0.0, game_fens, 1) if bot1_white else (0.0, 1.0, game_fens, 1)
    elif result == '0-1':
        return (0.0, 1.0, game_fens, -1) if bot1_white else (1.0, 0.0, game_fens, -1)
    else:
        return (0.5, 0.5, game_fens, 0)

def play_game_wrapper(args):
    b1, b2, is_white, record_moves = args
    return play_game(b1, b2, is_white, record_moves)

class Tournament:
    def __init__(self, bot1, bot2, amount):
        self.bot1 = bot1
        self.bot2 = bot2
        self.bot1_name = bot1.__class__.__name__
        self.bot2_name = bot2.__class__.__name__
        self.amount = amount
        self.mt_dict = {}
        
    def run(self, record_mt_dict=False):
        bot1_score = 0.0
        bot2_score = 0.0
        bot1_wins = 0
        bot2_wins = 0
        draws = 0
        completed_games = 0
        
        games_config = []
        for i in range(self.amount):
            bot1_is_white = (i < self.amount / 2)
            games_config.append((self.bot1, self.bot2, bot1_is_white, record_mt_dict))
            
        start_time = time.time()
        num_cores = multiprocessing.cpu_count()
        
        # temporary dictionary
        temp_dict = {} 
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=num_cores) as executor:
            future_to_game = {executor.submit(play_game_wrapper, config): config for config in games_config}
            
            for future in concurrent.futures.as_completed(future_to_game):
                score1, score2, game_fens, fen_score = future.result()
                
                bot1_score += score1
                bot2_score += score2
                
                if score1 == 1.0:
                    bot1_wins += 1
                elif score2 == 1.0:
                    bot2_wins += 1
                elif score1 == 0.5:
                    draws += 1
                        
                completed_games += 1
                
                if record_mt_dict:
                    for fen in game_fens:
                        if fen not in temp_dict:
                            temp_dict[fen] = [0, 0]
                        temp_dict[fen][0] += fen_score
                        temp_dict[fen][1] += 1
                
                self._print_progress(completed_games, bot1_score, bot2_score, draws)

        print("\n\n\n" + "=" * 50)
        print("RESULTS:\n")
        print(f"Time taken: {time.time() - start_time:.2f} seconds\n")
        
        self._print_results_bar(bot1_wins, bot2_wins, draws)
        print()
        print(f"{self.bot1_name} score: {bot1_score}")
        print(f"{self.bot2_name} score: {bot2_score}\n")

        if bot1_score > bot2_score:
            print(f"WINNER: {self.bot1_name}!")
        elif bot2_score > bot1_score:
            print(f"WINNER: {self.bot2_name}!")
        else:
            print("WINNER: Tie!")
        print("=" * 50)

        if record_mt_dict:
            for fen, (total_score, count) in temp_dict.items():
                self.mt_dict[fen] = (total_score / count, count)
        









    def _print_progress(self, completed, score1, score2, draws):
        if self.amount == 0:
            return
        percent = (completed / self.amount) * 100
        length = 30
        filled_length = int(length * completed // self.amount)
        bar = '█' * filled_length + '-' * (length - filled_length)
        print(f"\rProgress: |{bar}| {percent:.2f}% | {self.bot1_name}: {score1} | Draws: {draws} | {self.bot2_name}: {score2} |", end="", flush=True)

    def _print_results_bar(self, bot1_wins, bot2_wins, draws):
        bar_length = 50
        b1_len = int((bot1_wins / self.amount) * bar_length)
        d_len = int((draws / self.amount) * bar_length)
        b2_len = bar_length - b1_len - d_len 
        b1_char, d_char, b2_char = '█', '▒', '░'
        bar = (b1_char * b1_len) + (d_char * d_len) + (b2_char * b2_len)
        print(f"|{bar}|")
        print(f"{b1_char} {self.bot1_name} wins: {bot1_wins} | {d_char} Draws: {draws} | {b2_char} {self.bot2_name} wins: {bot2_wins}")