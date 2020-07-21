import math
import queue
import threading
import tkinter as tk
import enum
import numpy as np

from objects import *


def create_rect_topo(xsize, ysize):
    tiles = np.empty((xsize, ysize), dtype=object)

    for y in range(ysize):
        for x in range(xsize):
            tiles[x, y] = tile = TopoTile()

            if x > 0:
                other = tiles[x - 1, y]
                vector = np.array([-1, 0])

                other.add_neighbour(tile, -vector)
                tile.add_neighbour(other, vector)

            if y > 0:
                other = tiles[x, y - 1]
                vector = np.array([0, -1])

                other.add_neighbour(tile, -vector)
                tile.add_neighbour(other, vector)

            if x > 0 and y > 0:
                other = tiles[x - 1, y - 1]
                vector = np.array([-1, -1])

                other.add_neighbour(tile, -vector)
                tile.add_neighbour(other, vector)

            if x < xsize - 1 and y > 0:
                other = tiles[x + 1, y - 1]
                vector = np.array([1, -1])

                other.add_neighbour(tile, -vector)
                tile.add_neighbour(other, vector)

    centre = tiles[xsize // 2, ysize // 2]
    tiles = tiles.flatten()

    return TopoBoard(tiles, [(centre, tiles)])


# requires GameAuto#root
def create_window(game):
    game.root = tk.Tk()


# def resize(event=None):
    #     board_wid.draw()
    #    game.root.bind("<Configure>", resize)


# requires BoardWidget#board
def click_board(event=None):
    x, y = board_wid.map_to_board(event.x, event.y)
    click(x, y)


# requires GameAuto#clicked
def click(x, y):
    if game.clicked:
        validate_move(*game.clicked, x, y)
        unselect(*game.clicked)
        game.clicked = None
    else:
        game.clicked = x, y
        select(x, y)


# requires GameAuto#clicked_tile
def select(x, y):
    x1, y1 = board_wid.map_from_board(x, y)
    x2, y2 = board_wid.map_from_board(x + 1, y + 1)

    game.clicked_tile = board_wid.create_rectangle(x1, y1, x2, y2, fill="yellow")


# requires GameAuto#clicked_tile
def unselect(x, y):
    board_wid.delete(game.clicked_tile)
    game.clicked_tile = None


# requires GameAuto#board
# requires SquareBoard#get
# requires Tile#piece
# requires Piece#owner
# requires Piece#key
def pawn_rule(x1, y1, x2, y2):
    piece = game.board.get((x1, y1)).piece

    dy = 1 if piece.owner == "white" else -1

    if y2 - y1 == dy:
        pawn_rule2(x1, y1, x2, y2)


def pawn_rule2(x1, y1, x2, y2):
    if x1 == x2:
        pawn_rule3(x1, y1, x2, y2)
    elif x1 == x2 + 1 or x1 == x2 - 1:
        pawn_rule4(x1, y1, x2, y2)


def pawn_rule3(x1, y1, x2, y2):
    if not game.board.get((x2, y2)).piece:
        execute_move(x1, y1, x2, y2)


def pawn_rule4(x1, y1, x2, y2):
    if game.board.get((x2, y2)).piece:
        execute_move(x1, y1, x2, y2)


def execute_move(x1, y1, x2, y2):
    game.board.get((x2, y2)).piece = game.board.get((x1, y1)).piece
    game.board.get((x1, y1)).piece = None

    change_turn(game)

    board_wid.draw()


piece_rules = {"P": pawn_rule}


# requires piece_rules
def validate_move(x1, y1, x2, y2):
    piece = game.board.get((x1, y1)).piece

    if piece:
        if piece.owner == game.turn:
            piece_rules[piece.key](x1, y1, x2, y2)


# requires GameAuto#turn
def change_turn(game):
    game.turn = "white" if game.turn == "black" else "black"


# move this to main.py
game = GameAuto()

create_window(game)

game.load_board(create_rect_topo(8, 8))

board_wid = TopoBoardWidget(game.root, game.board)
board_wid.pack(fill=tk.BOTH, expand=True)

# game.board.tiles[3, 2].piece = Piece("P", "white")
# game.board.tiles[4, 5].piece = Piece("P", "black")

board_wid.bind("<Button-1>", click_board)

game.root.after(100, board_wid.draw)


game.root.mainloop()
# game.load_pieces(PieceTypes)


# ==========
# LOOP
# ==========

def load_interrupt_loop(game):
    game.running = True
    game.lock = threading.Condition()
    game.event = None
    game.interrupt_handler = None


def interrupt(sender, data, game):
    game.event = (sender, data)

    with game.lock:
        game.lock.notify()


def start(game):
    def f():
        with game.lock:
            while game.running:
                game.lock.wait()
                game.interrupt_handler(game.event)

    game_thread = threading.Thread(target=f)
    game_thread.run()


def make_turn_based(game):
    game.turn = None


# ===========
# INPUT
# ===========
def set_buffer_input(game):
    game.input_buffer = []


def set_click_interrupt(game):
    ...  # tk bind click to interrupt


def set_bufferers(game, input_validator, move_validator):
    game.input_validator = input_validator
    game.move_validator = move_validator
    game.interrupt_handler = buffer_event


def buffer_event(game, event):
    game.input_validator(game, event)
    game.move_validator(game)


def reset_buffer(game):
    game.input_buffer = []
