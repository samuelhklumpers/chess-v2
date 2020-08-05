import queue
import tkinter as tk
import numpy as np


class SelectMoveBuffer:
    def __init__(self):
        self.game = None
        self.buf = None
        self.move_target = None
        self.select_display = None


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
            click(self.game, self.drawn_tiles[items[0]])

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


def interrupt_game(game, interrupt):
    with game.cond:
        game.interrupt = interrupt
        game.cond.notify()


def click(game, tile):
    interrupt_game(game, ("click", tile))


def put_two(clickbuf, click):
    if clickbuf.buf:
        clickbuf.select_display.colour(clickbuf.buf, "gray")
        clickbuf.move_target.move(clickbuf.buf, click)
        clickbuf.buf = None
        clickbuf.game.root.after(0, clickbuf.select_display.draw)
    else:
        clickbuf.buf = click
        clickbuf.select_display.colour(click, "red")


def local_interrupt_handler(game):
    if game.interrupt[0] == "click":
        put_two(game.ibuf, game.interrupt[1])


def make_local(game):
    set_interrupt_handler(game, local_interrupt_handler)

    def shutdown():
        game.running = False
        interrupt_game(game, ("exit", 0))

    game.shutdown = shutdown


def set_interrupt_handler(game, handler):
    game.interrupt_handler = handler