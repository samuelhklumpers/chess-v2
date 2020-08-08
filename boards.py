from functools import partial

import numpy as np
import itertools as itr

from core import get_turn
from pieces import piece_move_iter


class Topology:
    def __init__(self, tiles, atlas, game):
        self.tiles = tiles
        self.atlas = atlas
        self.circle = 2 * np.pi
        self.epsilon = 1e-5
        self.game = game

    def get_charts(self, tile):
        return [chart for chart in self.atlas if tile in chart.tiles]

    def angle(self, a, b):
        return np.arccos(np.dot(a, b) / np.linalg.norm(a) / np.linalg.norm(b))

    def is_angle(self, a, b, circle_frac):
        return abs(self.angle(a, b) / self.circle - circle_frac) < self.epsilon


class Chart:
    def __init__(self, base, tiles):
        self.base = base
        self.tiles = tiles


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
        self.move = partial(move, self)


def get_moves(state, a, piece):
    return itr.islice(piece_move_iter(piece, state.topo, a), state.limit)


def move(state, a, b):
    piece = a.piece

    if not piece:
        return False

    if piece.owner != get_turn(state.game):
        return False

    for result_b, result_f in get_moves(state, a, piece):
        if b == result_b:
            result_f(state)

            return True

    return False


def find_checked_tiles(topo):
    ...  # mark all checked tiles in ChessState.move
