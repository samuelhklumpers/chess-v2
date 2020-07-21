# a window
# a playfield widget
# a board
# pieces
# a gameplay loop
# rules
# win condition


class BoardWidget(tk.Canvas):
    def __init__(self, board):
        tk.Canvas.__init__(self)

        self.board = board


class Board:
    def __init__(self):
        self.tiles = []
        self.neighbours = {}  # tile : [tile]
        # make f
        self.metric = {}  # tile : {neighbour1: {neighbour2: angle}}  # angle ~ dr_ij g dr_ik
        # make f


class Tile:
    def __init__(self):
        self.state = ...  # empty, piece, other


class State:
    ...


class SimpleState:
    def __init__(self, piece=None):
        self.piece = piece


class Piece:
    ...


class Pawn(Piece):
    ...


class Game:
    def start(self):
        ...


class TurnBasedGame(Game):
    def start(self):
        while True:
            # turn
            # rules
            # state transition
            ...


class TurnInstance(Game):
    def start(self):
        while True:
            # turn A
            # retry until rule valid

            turnA = ""


class Rule:
    ...  # InputAction -> OutputAction


class ForceSingleRule(Rule):
    def __init__(self, rules):
        self.rules = rules

    def check(self, game, action):
        for rule in self.rules:
            r = rule.check(action)

            if not isinstance(r, IdAction):
                r.act(game, action)


# game, player, click -> input stack
# scheduler: events
# input event -> stack processor
# processor: rules
# rule: game, stack -> action or Id

# click on board rule: stack=[S|T] -> S on board ? player rule(game, stack) : stack=T
# player: game=(turn=X, ...), stack=[(inp, player)|T] -> player = turn ? select rule(game, stack) : stack=T
# player: game=(select=Y, ...), stack[(inp, player)|T] ->
#   select = None ? select = (inp, player) :
#       (select = (inp, player) ? select = None, stack = T : valid rule(game, stack))
# valid: valid ? output rule : stack=T, select=None

class TurnRuleInstance(Rule):
    def __init__(self, player, processor):
        self.player = player

    def check(self, game, action):
        if game.turn == self.player:
            ...


class Action:
    def act(self, game, inp_action):
        ...  # Game -> Game


class IdAction(Action):
    def act(self, game, inp_action):
        return game

# thm 1: rule equiv action?
# yes, but checking saves operations
