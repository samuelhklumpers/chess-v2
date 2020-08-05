import numpy as np


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