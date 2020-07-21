import math
import queue
import tkinter as tk
import enum
import numpy as np

class Game:
    ...


# automaton based programming
class GameAuto:
    def __init__(self):
        self.root = None

        self.board = None

        self.turn = "white"

        self.clicked = None
        self.clicked_tile = None

    # requires GameAuto#board
    def load_board(self, board):
        self.board = board  # load topology, optionally drawing hints


class Tile:
    def __init__(self):
        self.piece = None


class SquareBoard:
    def __init__(self, xsize, ysize):
        self.tiles = np.empty((xsize, ysize))
        self.tiles = np.vectorize(lambda x: Tile())(self.tiles)

    # requires SquareBoard#tiles
    def get(self, pos):
        return self.tiles[pos]


class TopoTile:
    def __init__(self):
        self.neighbours = {}

    def angle(self, a, b):
        return np.arccos(np.dot(self.neighbours[a], self.neighbours[b]) / np.linalg.norm(a) / np.linalg.norm(b))

    def add_neighbour(self, other, vector):
        self.neighbours[other] = vector


class TopoBoard:
    def __init__(self, tiles, patches):
        self.tiles = tiles
        self.patches = patches


class TopoBoardWidget(tk.Canvas):
    def __init__(self, master, topo):
        tk.Canvas.__init__(self, master)

        self.topo = topo
        self.r = 20

    def draw(self):
        self.delete("all")

        width, height = self.winfo_width(), self.winfo_height()

        n = len(self.topo.patches)
        L = int(math.ceil(n ** 0.5))

        for i, patch in enumerate(self.topo.patches):
            dx = width / L * ((i % L) + 0.5)
            dy = height / L * ((i // L) + 0.5)

            self.draw_patch(patch, dx, dy)

    def draw_patch(self, patch, dx, dy):
        centre, points = patch
        visited = []

        q = queue.Queue()

        q.put((centre, dx, dy))
        visited += [centre]

        while not q.empty():
            p, x, y = q.get()

            self.create_oval(x - 4, y - 4, x + 4, y + 4, outline="black")

            for n in p.neighbours:
                if n in points:
                    dx, dy = self.r * p.neighbours[n][:2]

                    self.create_line(x, y, x + dx, y + dy, fill="black")

                    if n not in visited:
                        visited += [n]
                        q.put((n, x + dx, y + dy))


class BoardWidget(tk.Canvas):
    def __init__(self, master, board):
        tk.Canvas.__init__(self, master)

        self.board = board

    # always need a consistent draw-input pair
    # requires BoardWdiget#board
    def draw(self):
        self.delete("all")

        width, height = self.winfo_width(), self.winfo_height()

        xsize, ysize = self.board.tiles.shape

        dx = width / xsize
        dy = height / ysize

        color = ["red", "blue"]

        for i in range(xsize):
            for j in range(ysize):
                c = (i + j) % 2
                c = color[c]

                self.create_rectangle(i * dx, j * dy, (1 + i) * dx, (1 + j) * dy, fill=c)

                if self.board.tiles[i, j].piece:
                    self.create_text((i + 0.5) * dx, (j + 0.5) * dy, text=self.board.tiles[i, j].piece.key, fill="green")

    # requires SquareBoard#tiles.shape
    def map_to_board(self, x_p, y_p):
        xsize, ysize = self.board.tiles.shape
        width, height = self.winfo_width(), self.winfo_height()
        return int(xsize * x_p / width), int(ysize * y_p / height)

    def map_from_board(self, x_b, y_b):
        xsize, ysize = self.board.tiles.shape
        width, height = self.winfo_width(), self.winfo_height()
        return int(x_b / xsize * width), int(y_b / ysize * height)


class Piece:
    def __init__(self, key, owner):
        self.key = key
        self.owner = owner
