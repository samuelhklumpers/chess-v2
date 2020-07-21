import threading

from objects import *
from rules import *


game = Game()


# load tk
def make_single_window_app(game):
    game.root = tk.Tk()


make_single_window_app(game)

# load topo widget
# set_topo(game, topo)

def make_topo_chess(game, topo):
    game.topo = topo


def add_main_widget_topo(game):
    ...

# load chess


# start loop
def simple_chess_click_validator(game, event):
    if event.type == tk.EventType.ButtonPress and event.num == 1:
        if len(game.buffer) == 0:
            if clicked_piece(game, event):
                game.buffer += [event]
        elif len(game.buffer) == 1:
            if clicked_tile(game, event):
                game.buffer += [event]


def clicked_piece(game, event):
    ...


def clicked_tile(game, event):
    ...


def simple_chess_validate_move(game):
    ...


load_interrupt_loop(game)
set_buffer_input(game)
set_bufferers(game, simple_chess_click_validator, simple_chess_validate_move)
make_turn_based(game)
start(game)
