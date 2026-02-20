import time
import concurrent.futures
import chess
import os
import sys
import chess.pgn
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from logic.board import Board

def play_game(bot1, bot2, bot1_white):
    board = Board()

    white_bot = bot1 if bot1_white else bot2
    black_bot = bot2 if bot1_white else bot1
    
    white_bot.set_color(chess.WHITE)
    black_bot.set_color(chess.BLACK)
    
    while not board.is_game_over():
        if board.is_turn:
            move = white_bot.get_move(board)
        else:
            move = black_bot.get_move(board)

        if move is None:
            break
        
        board.move_piece(move[0], move[1])
        
    result = board.engine.result()

    pgn = chess.pgn.Game.from_board(board.engine)
    pgn.headers["White"] = white_bot.__class__.__name__
    pgn.headers["Black"] = black_bot.__class__.__name__
    pgn.headers["Result"] = result
    pgn = str(pgn)
    
    # in the chess library: 1-0 = white wins, 0-1 = black wins, 1/2-1/2 = draw
    if result == '1-0':
        return (1.0, 0.0, pgn) if bot1_white else (0.0, 1.0, pgn)
    elif result == '0-1':
        return (0.0, 1.0, pgn) if bot1_white else (1.0, 0.0, pgn)
    else:
        return (0.5, 0.5, pgn)

class Tournament:
    def __init__(self, bot1, bot2, bot1_name, bot2_name, amount):
        self.bot1 = bot1
        self.bot2 = bot2
        self.bot1_name = bot1_name
        self.bot2_name = bot2_name
        self.amount = amount
        
    def run(self):
        print(f"Starting Tournament: {self.bot1_name} vs {self.bot2_name}")
        print(f"Total Games: {self.amount}")
        
        bot1_score = 0.0
        bot2_score = 0.0
        bot1_wins = 0
        bot2_wins = 0
        draws = 0
        completed_games = 0
        history = []
        
        games_config = []
        for i in range(self.amount):
            bot1_is_white = (i < self.amount / 2)
            games_config.append((self.bot1, self.bot2, bot1_is_white))
            
        start_time = time.time()
        self._print_progress(0, bot1_score, bot2_score, draws)
        
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = [executor.submit(play_game, b1, b2, is_white) for b1, b2, is_white in games_config]
            
            for future in concurrent.futures.as_completed(futures):
                score1, score2, pgn = future.result()
                bot1_score += score1
                bot2_score += score2
                
                # Track actual wins for the results bar
                if score1 == 1.0:
                    bot1_wins += 1
                elif score2 == 1.0:
                    bot2_wins += 1
                elif score1 == 0.5:
                    draws += 1
                        
                completed_games += 1
                history.append(pgn)
                self._print_progress(completed_games, bot1_score, bot2_score, draws)

        print()
        print()
        print()
        print("=" * 50)
        print("RESULTS:")
        print()

        print(f"Time taken: {time.time() - start_time:.2f} seconds")
        print()

        self._print_results_bar(bot1_wins, bot2_wins, draws)
        print()

        print(f"{self.bot1_name} score: {bot1_score}")
        print(f"{self.bot2_name} score: {bot2_score}")
        print()

        if bot1_score > bot2_score:
            print(f"WINNER: {self.bot1_name}!")
        elif bot2_score > bot1_score:
            print(f"WINNER: {self.bot2_name}!")
        else:
            print("WINNER: Tie!")
        print("=" * 50)

        return history
        

    def _print_progress(self, completed, score1, score2, draws):
        if self.amount == 0:
            return
        percent = (completed / self.amount) * 100
        length = 30
        filled_length = int(length * completed // self.amount)
        bar = '█' * filled_length + '-' * (length - filled_length)
        print(f"\rProgress: |{bar}| {percent:.2f}% | {self.bot1_name}: {score1} | {self.bot2_name}: {score2} | Draws: {draws} |", end="", flush=True)

    def _print_results_bar(self, bot1_wins, bot2_wins, draws):
        bar_length = 50
        
        b1_len = int((bot1_wins / self.amount) * bar_length)
        d_len = int((draws / self.amount) * bar_length)
        b2_len = bar_length - b1_len - d_len 
        
        b1_char = '█'
        d_char = '▒'
        b2_char = '░'
        
        bar = (b1_char * b1_len) + (d_char * d_len) + (b2_char * b2_len)
        
        print(f"|{bar}|")
        print(f"{b1_char} {self.bot1_name} wins: {bot1_wins} | {d_char} Draws: {draws} | {b2_char} {self.bot2_name} wins: {bot2_wins}")