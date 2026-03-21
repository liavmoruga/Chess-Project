from src.logic.bots import RandomBot, MaterialBot, SmartBot
from src.ui.game import ChessGame
from src.logic.tournament import Tournament
import pickle


def main(num):
    if num == 1:
        g = ChessGame(white_agent=None, black_agent=SmartBot(3))
        g.run()

    elif num == 2:
        t = Tournament(MaterialBot(3), RandomBot(), 100)
        mt = t.run(False)
        # with open("mt.pkl", 'wb') as file:
        #     pickle.dump(mt, file)




if __name__ == "__main__":
    main(1)

#make a place to store pkl and keras
# make the bots classes stateless / static and they take as an input a color so they can work in multiple proccesses