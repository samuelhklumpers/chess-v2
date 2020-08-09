import copy
from functools import partial

import numpy as np
import itertools as itr

from core import get_turn
from pieces import piece_move_iter


class Topology:
    def __init__(self, tiles, atlas, state):
        self.tiles = tiles
        self.atlas = atlas
        self.circle = 2 * np.pi
        self.epsilon = 1e-5
        self.state = state

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
    def __init__(self):
        self.topo = None
        self.limit = 100
        self.move = partial(move2, self)
        self.turn = 0
        self.players = 2


def get_moves(topo, a, piece, limit):
    return itr.islice(piece_move_iter(piece, topo, a), limit)


def move(state, a, b):
    piece = a.piece

    if not piece:
        return False

    if piece.owner != get_turn(state):
        return False

    for result_b, result_f in get_moves(state.topo, a, piece, state.limit):
        if b == result_b:
            result_f(state)

            return True

    return False


def move_by_index(state, i, j):
    a = state.topo.tiles[i]
    b = state.topo.tiles[j]

    piece = a.piece

    if not piece:
        return False

    if piece.owner != get_turn(state):
        return False

    for result_b, result_f in get_moves(state.topo, a, piece, state.limit):
        if b == result_b:
            result_f(state)

            find_checked_tiles(state, state.topo)

            return True

    return False


def move2(state, a, b):
    piece = a.piece

    if not piece:
        return False

    if piece.owner != get_turn(state):
        return False

    for result_b, result_f in get_moves(state.topo, a, piece, state.limit):
        if b == result_b:
            # I hate this
            temp_state = copy.deepcopy(state)
            i = next(i for i, x in enumerate(state.topo.tiles) if x == a)
            j = next(i for i, x in enumerate(state.topo.tiles) if x == b)

            move_by_index(temp_state, i, j)

            would_check = False
            for temp_tile in temp_state.topo.tiles:
                p = temp_tile.piece

                if p and p.shape == "K" and p.owner == get_turn(state):
                    if any(c.owner != p.owner for c in temp_tile.checks):
                        would_check = True
                        break

            if would_check:
                continue

            result_f(state)

            find_checked_tiles(state, state.topo)

            return True

    return False


def add_checked(tile):
    tile.checks = []


def find_checked_tiles(state, topo):
    for tile in topo.tiles:
        tile.checks = []

    # should probably store all living pieces somewhere else lol
    for tile in topo.tiles:
        piece = tile.piece

        if piece:
            for target, f in get_moves(topo, tile, piece, state.limit):
                target.checks.append(piece)
