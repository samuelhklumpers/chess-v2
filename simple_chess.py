import queue
import tkinter as tk
import numpy as np
import threading
import itertools as itr


class SimpleChess:
    def __init__(self):
        self.root = None
        self.topo = None
        self.topo_widget = None
        self.turn = 0
        self.clicked = None
        self.cond = None
        self.interrupt = None
        self.running = False
        self.chess_state = None
        self.ibuf = None

    def do_root(self):
        self.root = tk.Tk()
        self.root.geometry("600x600")

    def set_topo(self, topo):
        self.topo = topo

    def do_topo_widget(self):
        self.topo_widget = TopoWidget(self, self.root, self.topo)
        self.topo_widget.layout()
        self.topo_widget.pack(expand=True, fill=tk.BOTH)

    def click(self, tile):
        self.interrupt_game(("click", tile))

    def set_input_buffer(self, ibuf):
        self.ibuf = ibuf
        self.ibuf.game = self
        self.ibuf.display = self.topo_widget
        self.ibuf.target = self.chess_state

    def game_thread(self):
        self.running = True

        self.cond = threading.Condition()

        with self.cond:
            while self.running:
                self.cond.wait()

                if self.interrupt[0] == "click":
                    self.ibuf.put(self.interrupt[1])

    def load_chess_state(self, state):
        state.topo = self.topo
        self.chess_state = state

    def interrupt_game(self, interrupt):
        with self.cond:
            self.interrupt = interrupt
            self.cond.notify()

    def run(self):
        threading.Thread(target=self.game_thread).start()

        self.root.mainloop()


class SelectMoveBuffer:
    def __init__(self):
        self.game = None
        self.buf = None
        self.target = None
        self.display = None

    def put(self, click):
        if self.buf:
            self.display.colour(self.buf, "gray")
            self.target.move(self.buf, click)
            self.buf = None
            self.game.root.after(0, self.display.draw)
        else:
            self.buf = click
            self.display.colour(click, "red")


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


class TopoWidget(tk.Canvas):
    def __init__(self, game, master, topo):
        tk.Canvas.__init__(self, master)

        self.game = game
        self.topo = topo
        self.charts = None
        self.atlas_to_widgets = {}

    def layout(self):
        self.bind("<Expose>", self.draw)

        N = len(self.topo.atlas)

        L = int(np.ceil(np.sqrt(N)))

        self.charts = np.empty((L, L), dtype=object)

        for i in range(L):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        for i in range(N):
            x = i % L
            y = i // L

            self.charts[x, y] = ChartWidget(self.game, self, self.topo.atlas[i])
            self.charts[x, y].grid(row=x, column=y, sticky="nsew")
            self.charts[x, y].setup()

            self.atlas_to_widgets[self.topo.atlas[i]] = self.charts[x, y]

    def draw(self, event=None):
        for chart in self.charts.flat:
            if chart:
                chart.draw()

    def colour(self, tile, c):
        for chart in self.topo.get_charts(tile):
            self.atlas_to_widgets[chart].colour(tile, c)


class ChartWidget(tk.Canvas):
    def __init__(self, game, master, chart):
        tk.Canvas.__init__(self, master)

        self.game = game
        self.chart = chart
        self.drawn_tiles = {}
        self.tile_to_item = {}

    def setup(self):
        self.config(bd=1, highlightbackground="black", highlightcolor="black")
        self.bind("<Button-1>", self.send_tile)

    def send_tile(self, event):
        x, y = event.x, event.y

        items = self.find_overlapping(x, y, x, y)
        items = [item for item in items if item in self.drawn_tiles]

        if items:
            self.game.click(self.drawn_tiles[items[0]])

    def colour(self, tile, c):
        self.itemconfig(self.tile_to_item[tile], fill=c)

    def draw(self):
        self.delete("all")

        self.drawn_tiles = {}

        dr = 40
        R = dr / 4
        dx, dy = self.winfo_width() / 2, self.winfo_height() / 2

        base = self.chart.base
        tiles = self.chart.tiles
        visited = []

        q = queue.Queue()
        q.put((base, dx, dy))
        visited += [base]

        while not q.empty():
            current, x, y = q.get()

            item = self.create_oval(x - R, y - R, x + R, y + R, outline="black", fill="gray")
            self.drawn_tiles[item] = current
            self.tile_to_item[current] = item

            if current.piece:
                piece = current.piece
                c = "black" if piece.owner == 1 else "white"

                self.create_text(x, y, text=piece.shape, fill=c)

            for neigh in current.neighs:
                dx, dy = dr * current.neighs[neigh][:2]

                dl = np.sqrt(dx ** 2 + dy ** 2)

                x1 = x + R * dx / dl
                y1 = y + R * dy / dl
                x2 = x + dx - R * dx / dl
                y2 = y + dy - R * dy / dl

                self.create_line(x1, y1, x2, y2, fill="black")

                if neigh in tiles and neigh not in visited:
                    visited += [neigh]
                    q.put((neigh, x + dx, y + dy))


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

    game.do_root()

    topo = create_normal_board()

    game.set_topo(topo)

    game.do_topo_widget()

    game.load_chess_state(ChessState(game))

    game.set_input_buffer(SelectMoveBuffer())

    game.run()


do_simple_chess()
