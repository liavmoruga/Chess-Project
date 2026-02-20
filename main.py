from bots.material_bot import MaterialBot
from bots.random_bot import RandomBot
from ui.game import ChessGame
from logic.tournament import Tournament


if __name__ == "__main__":
    #game = ChessGame(white_agent=None, black_agent=MaterialBot(3))
    #game.run()

    tournament = Tournament(
        bot1=MaterialBot(2),
        bot2=RandomBot(0),
        bot1_name="Material Bot",
        bot2_name="Random Bot",
        amount=100)
    histroy = tournament.run()
