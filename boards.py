import numpy as np
import itertools as itr

from pieces import piece_move_iter


class Topology:
    def __init__(self, tiles, atlas):
        self.tiles = tiles
        self.atlas = atlas
        self.circle = 2 * np.pi
        self.epsilon = 1e-5

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

            piece.moved = True

            self.game.turn = 1 - self.game.turn


def checked_tiles(topo):
    ...  # mark all checked tiles in ChessState.move
