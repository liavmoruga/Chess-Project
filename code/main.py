from bots.minimax import MaterialBot
from bots.random_bot import RandomBot
from ui.game import ChessGame
from training.tournament import Tournament
from training.montecarlo import train_and_save_model
import pickle
from bots.montecarlo_bot import MonteCarloBot

if __name__ == "__main__":
    # g = ChessGame(white_agent=None, black_agent=MonteCarloBot())
    # g.run()

    t = Tournament(MonteCarloBot(), RandomBot(0), 100)
    mt = t.run(False)

    # with open("montecarlo.pkl", 'wb') as file:
    #     pickle.dump(mt, file)

    #train_and_save_model()
