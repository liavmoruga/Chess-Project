from bots.material_bot import MaterialBot
from bots.random_bot import RandomBot
from ui.game import ChessGame
from training.tournament import Tournament


if __name__ == "__main__":
    game = ChessGame(white_agent=None, black_agent=MaterialBot(6))
    history = game.run()
    print(history)

    # tournament = Tournament(
    #     bot1=RandomBot(0),
    #     bot2=RandomBot(0),
    #     amount=1000)
    # histroy = tournament.run()