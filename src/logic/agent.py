# AGENT INTERFACE

class Agent:
    def __init__(self):
        self.color = None

    def set_color(self, color):
        self.color = color

    def get_move(self, board_obj):
        raise NotImplementedError