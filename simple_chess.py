import queue
import numpy as np
import itertools as itr

from boards import Topology, Chart
from core import SimpleChess, set_window, set_topo, set_input_buffer, do_topo_widget, load_chess_state, run_game,\
    game_thread
from online import make_online
from ui import SelectMoveBuffer, make_local


class Tile:
    def __init__(self):
        self.piece = None
        self.neighs = {}

    def add_neigh(self, neigh, vector):
        self.neighs[neigh] = vector
        neigh.neighs[self] = -vector


class ChessState:
    def __init__(self, game):
        self.topo = None
        self.limit = 100
        self.game = game

    def get_moves(self, a, piece):
        return itr.islice(piece_move_iter(piece, self.topo, a), self.limit)

    def move(self, a, b):
        piece = a.piece

        if not piece:
            return

        if piece.owner != self.game.turn:
            return

        if b in self.get_moves(a, piece):
            a.piece = None
            b.piece = piece

            self.game.turn = 1 - self.game.turn


def piece_move_iter(piece, topo, tile):
    if piece.shape == "K":
        return king_move_iter(piece, topo, tile)
    elif piece.shape == "Q":
        return queen_move_iter(piece, topo, tile)
    elif piece.shape == "R":
        return rook_move_iter(piece, topo, tile)
    elif piece.shape == "B":
        return bishop_move_iter(piece, topo, tile)
    elif piece.shape == "k":
        return knight_move_iter(piece, topo, tile)
    elif piece.shape == "p":
        return pawn_move_iter(piece, topo, tile)


class Piece:
    def __init__(self, shape, owner):
        self.shape = shape
        self.owner = owner


def king_move_iter(piece, topo, tile):
    yield from tile.neighs


def queen_move_iter(piece, topo, tile):
    q = queue.Queue()

    for neigh in tile.neighs:
        q.put((neigh, neigh.neighs[tile]))

    while not q.empty():
        tile, vec_in = q.get()

        yield tile

        for neigh, vec_out in tile.neighs.items():
            if topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile]))


def rook_move_iter(piece, topo, tile):
    q = queue.Queue()

    def angles(vec_out):
        return topo.is_angle(vec_out, [1, 0], 0)\
            or topo.is_angle(vec_out, [1, 0], 0.25)\
            or topo.is_angle(vec_out, [1, 0], 0.5)

    for neigh, vec_out in tile.neighs.items():
        if angles(vec_out):
            q.put((neigh, neigh.neighs[tile]))

    while not q.empty():
        tile, vec_in = q.get()

        yield tile

        for neigh, vec_out in tile.neighs.items():
            if angles(vec_out) and topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile]))


def bishop_move_iter(piece, topo, tile):
    q = queue.Queue()

    def angles(vec_out):
        return topo.is_angle(vec_out, [1, 0], 1 / 8) \
               or topo.is_angle(vec_out, [1, 0], 3 / 8)

    for neigh, vec_out in tile.neighs.items():
        if angles(vec_out):
            q.put((neigh, neigh.neighs[tile]))

    while not q.empty():
        tile, vec_in = q.get()

        yield tile

        for neigh, vec_out in tile.neighs.items():
            if angles(vec_out) and topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile]))


def knight_move_iter(piece, topo, tile):
    for step1 in tile.neighs:
        vec_in1 = step1.neighs[tile]

        for step2, vec_out1 in step1.neighs.items():
            if not topo.is_angle(vec_in1, vec_out1, 0.5):
                continue

            vec_in2 = step2.neighs[step1]

            for end, vec_out2 in step2.neighs.items():
                if topo.is_angle(vec_in2, vec_out2, 0.25):
                    yield end


def pawn_move_iter(piece, topo, tile):
    for neigh, vec in tile.neighs.items():
        m = 1 if piece.owner == 0 else -1

        if topo.is_angle(vec, [0, m], 0.0) and not neigh.piece:
            yield neigh
        elif 0 < topo.angle(vec, [0, m]) / topo.circle < 0.25 and neigh.piece:
            yield neigh


def create_normal_board():
    xsize = ysize = 8
    
    tiles = np.empty((xsize, ysize), dtype=object)

    for y in range(ysize):
        for x in range(xsize):
            tiles[x, y] = tile = Tile()

            if x > 0:
                tile.add_neigh(tiles[x - 1, y], np.array([-1, 0]))

            if y > 0:
                tile.add_neigh(tiles[x, y - 1], np.array([0, -1]))

            if x > 0 and y > 0:
                tile.add_neigh(tiles[x - 1, y - 1], np.array([-1, -1]))

            if x < xsize - 1 and y > 0:
                tile.add_neigh(tiles[x + 1, y - 1], np.array([1, -1]))

    for x in range(xsize):
        tiles[x, 1].piece = Piece("p", 0)
        tiles[x, 6].piece = Piece("p", 1)

    tiles[0, 0].piece = Piece("R", 0)
    tiles[7, 0].piece = Piece("R", 0)
    tiles[0, 7].piece = Piece("R", 1)
    tiles[7, 7].piece = Piece("R", 1)

    tiles[1, 0].piece = Piece("k", 0)
    tiles[6, 0].piece = Piece("k", 0)
    tiles[1, 7].piece = Piece("k", 1)
    tiles[6, 7].piece = Piece("k", 1)

    tiles[2, 0].piece = Piece("B", 0)
    tiles[5, 0].piece = Piece("B", 0)
    tiles[2, 7].piece = Piece("B", 1)
    tiles[5, 7].piece = Piece("B", 1)

    tiles[3, 0].piece = Piece("Q", 0)
    tiles[4, 0].piece = Piece("K", 0)
    tiles[3, 7].piece = Piece("Q", 1)
    tiles[4, 7].piece = Piece("K", 1)

    centre = tiles[xsize // 2, ysize // 2]
    tiles = tiles.flatten()

    return Topology(tiles, [Chart(centre, tiles)])


def do_simple_chess():
    game = SimpleChess()

    set_window(game)

    set_topo(game, create_normal_board())

    do_topo_widget(game)

    load_chess_state(game, ChessState(game))

    set_input_buffer(game, SelectMoveBuffer())

    make_local(game)

    game.thread_targets += [game_thread(game)]

    run_game(game)


def do_online_chess():
    game = SimpleChess()

    set_window(game)

    set_topo(game, create_normal_board())

    do_topo_widget(game)

    load_chess_state(game, ChessState(game))

    set_input_buffer(game, SelectMoveBuffer())

    addr = input("Remote address: ")
    rport = input("Remote port: ")
    lport = input("Local port: ")
    colour = input("Colour: ")

    game.thread_targets += [game_thread(game)]

    make_local(game)
    make_online(game, int(colour), addr, int(rport), int(lport))

    run_game(game)


do_online_chess()

