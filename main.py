from src.logic.bots import RandomBot
from src.ui.game import ChessGame
from src.logic.tournament import Tournament



def main(num):
    if num == 1:
        g = ChessGame(white_agent=None, black_agent=RandomBot(0))
        g.run()

    elif num == 2:
        t = Tournament(RandomBot(0), RandomBot(0), 100)
        t.run(False)



if __name__ == "__main__":
    main(1)
