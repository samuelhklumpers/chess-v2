import threading
import tkinter as tk

from ui import TopoWidget, put_two


class SimpleChess:
    def __init__(self):
        self.root = None
        self.topo = None
        self.topo_widget = None
        self.turn = 0
        self.players = 2
        self.clicked = None
        self.cond = None
        self.interrupt = None
        self.running = False
        self.chess_state = None
        self.ibuf = None
        self.interrupt_handler = None
        self.shutdown = None
        self.thread_targets = []


def get_turn(game):
    return game.turn % game.players


def set_window(game, geo="600x600"):
    game.root = tk.Tk()
    game.root.geometry(geo)


def set_topo(game, topo):
    game.topo = topo


def do_topo_widget(game):
    game.topo_widget = TopoWidget(game, game.root, game.topo)
    game.topo_widget.layout()
    game.topo_widget.pack(expand=True, fill=tk.BOTH)


def set_input_buffer(game, ibuf):
    game.ibuf = ibuf
    game.ibuf.game = game
    game.ibuf.select_display = game.topo_widget
    game.ibuf.move_target = game.chess_state


def game_thread(game):
    def f():
        game.running = True

        game.cond = threading.Condition()

        with game.cond:
            while game.running:
                game.cond.wait()

                game.interrupt_handler(game)

    return f


def load_chess_state(game, state):
    state.topo = game.topo
    game.chess_state = state


def run_game(game):
    threads = []

    for target in game.thread_targets:
        thread = threading.Thread(target=target)
        threads.append(thread)
        thread.start()

    game.root.mainloop()

    if game.shutdown:
        game.shutdown()

    for thread in threads:
        thread.join()
