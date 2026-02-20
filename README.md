# Chess Project - Liav Moruga

Hello there! Open main.py

Inside there you can run a game with a ui like that(None means local input):

game = ChessGame(white_agent=None, black_agent=MaterialBot(3))

game.run()

so here you can play against a friend locally, against a bot, or watch to bots play against each other

You can also run a tournament like that:

tournament = Tournament(
    bot1=MaterialBot(3),
    bot2=RandomBot(0),
    bot1_name="Material Bot",
    bot2_name="Random Bot",
    amount=100)

histroy = tournament.run()
