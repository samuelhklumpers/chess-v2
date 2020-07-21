import math
import queue
import tkinter as tk
import enum
import numpy as np


# automaton based programming
class GameAuto:
    def __init__(self):
        self.root = None

        self.board = None

        self.turn = "white"

        self.clicked = None
        self.clicked_tile = None

    # requires GameAuto#root
    def create_window(self):
        self.root = tk.Tk()

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

# def resize(event=None):
#     board_wid.draw()
# game.root.bind("<Configure>", resize)


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

    change_turn()

    board_wid.draw()


piece_rules = {"P": pawn_rule}


# requires piece_rules
def validate_move(x1, y1, x2, y2):
    piece = game.board.get((x1, y1)).piece

    if piece:
        if piece.owner == game.turn:
            piece_rules[piece.key](x1, y1, x2, y2)


# requires GameAuto#turn
def change_turn():
    game.turn = "white" if game.turn == "black" else "black"


game = GameAuto()

game.create_window()

game.load_board(create_rect_topo(8, 8))

board_wid = TopoBoardWidget(game.root, game.board)
board_wid.pack(fill=tk.BOTH, expand=True)

# game.board.tiles[3, 2].piece = Piece("P", "white")
# game.board.tiles[4, 5].piece = Piece("P", "black")

board_wid.bind("<Button-1>", click_board)

game.root.after(100, board_wid.draw)


game.root.mainloop()
# game.load_pieces(PieceTypes)




