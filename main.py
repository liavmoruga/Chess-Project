from code.bots.material_bot import MaterialBot
from code.bots.random_bot import RandomBot
from code.ui.game import ChessGame
from code.logic.tournament import Tournament



def main(num):
    if num == 1:
        g = ChessGame(white_agent=None, black_agent=MaterialBot(5))
        g.run()

    elif num == 2:
        t = Tournament(MaterialBot(2), RandomBot(0), 100)
        t.run(False)

    elif num == 3:
        t = Tournament(RandomBot(0), RandomBot(0), 100000)
        t.run(True)
        mt_dict = t.mt_dict



if __name__ == "__main__":
    main(2)
