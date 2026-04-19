from src.logic.bots import RandomBot, MaterialBot, SmartBot
from src.ui.game import ChessGame
from src.logic.tournament import Tournament
import pickle


def main(num):
    if num == 1:
        g = ChessGame(white_agent=MaterialBot(3, 2, 0.5), black_agent=MaterialBot(3, 2, 0.5))
        g.run()

    elif num == 2:
        t = Tournament(SmartBot(2), MaterialBot(2), 25)
        t.run(False)

    elif num == 3:
        t = Tournament(MaterialBot(2, 3, 0.5), MaterialBot(2, 3, 0.5), 10000)
        mt = t.run(True)
        with open("mt.pkl", 'wb') as file:
            pickle.dump(mt, file)




if __name__ == "__main__":
    main(1)
