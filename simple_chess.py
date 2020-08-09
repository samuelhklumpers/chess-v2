import numpy as np

from boards import Topology, Chart, Tile, ChessState, add_checked
from core import SimpleChess, set_window, set_topo, set_input_buffer, do_topo_widget, load_chess_state, run_game,\
    game_thread
from online import make_online
from pieces import Piece, create_piece, piece_move_iter
from ui import SelectMoveBuffer, make_local


def create_normal_board():
    xsize = ysize = 8
    
    tiles = np.empty((xsize, ysize), dtype=object)

    for y in range(ysize):
        for x in range(xsize):
            tiles[x, y] = tile = Tile()
            add_checked(tile)

            if x > 0:
                tile.add_neigh(tiles[x - 1, y], np.array([-1, 0]))

            if y > 0:
                tile.add_neigh(tiles[x, y - 1], np.array([0, -1]))

            if x > 0 and y > 0:
                tile.add_neigh(tiles[x - 1, y - 1], np.array([-1, -1]))

            if x < xsize - 1 and y > 0:
                tile.add_neigh(tiles[x + 1, y - 1], np.array([1, -1]))

    for x in range(xsize):
        tiles[x, 1].piece = create_piece("p", 0)
        tiles[x, 6].piece = create_piece("p", 1)

    tiles[0, 0].piece = create_piece("R", 0)
    tiles[7, 0].piece = create_piece("R", 0)
    tiles[0, 7].piece = create_piece("R", 1)
    tiles[7, 7].piece = create_piece("R", 1)

    tiles[1, 0].piece = create_piece("k", 0)
    tiles[6, 0].piece = create_piece("k", 0)
    tiles[1, 7].piece = create_piece("k", 1)
    tiles[6, 7].piece = create_piece("k", 1)

    tiles[2, 0].piece = create_piece("B", 0)
    tiles[5, 0].piece = create_piece("B", 0)
    tiles[2, 7].piece = create_piece("B", 1)
    tiles[5, 7].piece = create_piece("B", 1)

    tiles[3, 0].piece = create_piece("Q", 0)
    tiles[4, 0].piece = create_piece("K", 0)
    tiles[3, 7].piece = create_piece("Q", 1)
    tiles[4, 7].piece = create_piece("K", 1)

    centre = tiles[xsize // 2, ysize // 2]
    tiles = tiles.flatten()

    return Topology(tiles, [Chart(centre, tiles)], None)


class DrawSelect:
    def __init__(self):
        self.drawn = {"select": None, "moves": []}

    def draw(self, topo, click, display):
        self.drawn["select"] = click

        display.colour(click, "red")

        piece = click.piece

        if piece:
            for tile, _ in piece_move_iter(piece, topo, click):
                self.drawn["moves"] += [tile]

                display.colour(tile, "green")

    def undraw(self, display):
        display.colour(self.drawn["select"], "gray")

        for tile in self.drawn["moves"]:
            display.colour(tile, "gray")

        self.drawn = {"select": None, "moves": []}


def do_simple_chess():
    game = SimpleChess()

    set_window(game)

    topo = create_normal_board()
    set_topo(game, topo)

    do_topo_widget(game)

    load_chess_state(game, ChessState())
    topo.state = game.chess_state

    set_input_buffer(game, SelectMoveBuffer(DrawSelect()))

    make_local(game)

    game.thread_targets += [game_thread(game)]

    run_game(game)


def do_online_chess():
    game = SimpleChess()

    set_window(game)

    topo = create_normal_board()
    set_topo(game, topo)

    do_topo_widget(game)

    load_chess_state(game, ChessState())
    topo.state = game.chess_state

    set_input_buffer(game, SelectMoveBuffer(DrawSelect()))

    addr = input("Remote address: ")
    rport = input("Remote port: ")
    lport = input("Local port: ")
    colour = input("Colour: ")

    game.thread_targets += [game_thread(game)]

    make_local(game)
    make_online(game, int(colour), addr, int(rport), int(lport))

    run_game(game)


do_online_chess()

