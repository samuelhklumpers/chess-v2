import queue
import tkinter as tk
import numpy as np


class SimpleChess:
    def __init__(self):
        self.root = None
        self.topo = None
        self.topo_widget = None
        self.turn = 0
        self.clicked = None

    def do_root(self):
        self.root = tk.Tk()
        self.root.geometry("600x600")

    def set_topo(self, topo):
        self.topo = topo

    def do_topo_widget(self):
        self.topo_widget = TopoWidget(self.root, self.topo)

    def click(self, tile):
        print(tile.__dict__)


class Topology:
    def __init__(self, tiles, atlas):
        self.tiles = tiles
        self.atlas = atlas


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


class TopoWidget(tk.Canvas):
    def __init__(self, master, topo):
        tk.Canvas.__init__(self, master)

        self.topo = topo
        self.charts = None

    def layout(self):
        N = len(self.topo.atlas)

        L = int(np.ceil(np.sqrt(N)))

        self.charts = np.empty((L, L), dtype=object)

        for i in range(L):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)

        for i in range(N):
            x = i % L
            y = i // L

            self.charts[x, y] = ChartWidget(self, self.topo.atlas[i])
            self.charts[x, y].grid(row=x, column=y, sticky="nsew")
            self.charts[x, y].setup()

    def draw(self):
        for chart in self.charts.flat:
            if chart:
                chart.draw()


class ChartWidget(tk.Canvas):
    def __init__(self, master, chart):
        tk.Canvas.__init__(self, master)

        self.chart = chart
        self.drawn_tiles = {}

    def setup(self):
        self.config(bd=1, highlightbackground="black", highlightcolor="black")
        self.bind("<Button-1>", self.send_tile)

    def send_tile(self, event):
        x, y = event.x, event.y

        # doesn't work
        items = self.find_overlapping(x, y, x, y)
        items = [item for item in items if item in self.drawn_tiles]

        if items:
            self.master.master.click(self.drawn_tiles[items[0]])

    def draw(self):
        self.delete("all")

        self.drawn_tiles = {}

        dr = 20
        dx, dy = self.winfo_width() / 2, self.winfo_height() / 2

        base = self.chart.base
        tiles = self.chart.tiles
        visited = []

        q = queue.Queue()
        q.put((base, dx, dy))
        visited += [base]

        while not q.empty():
            current, x, y = q.get()

            self.drawn_tiles[current] = self.create_oval(x - 4, y - 4, x + 4, y + 4, outline="black")

            for neigh in current.neighs:
                if neigh in tiles:
                    dx, dy = dr * current.neighs[neigh][:2]

                    self.create_line(x, y, x + dx, y + dy, fill="black")

                    if neigh not in visited:
                        visited += [neigh]
                        q.put((neigh, x + dx, y + dy))


def test():
    root = tk.Tk()
    root.geometry("400x400")

    a = Tile()
    b = Tile()
    c = Tile()

    a.add_neigh(b, np.array([1, 0]))
    b.add_neigh(a, np.array([-1, 0]))

    b.add_neigh(c, np.array([0, 1]))
    c.add_neigh(b, np.array([0, -1]))

    topo = Topology([a, b, c], [Chart(b, [a, b]), Chart(b, [b, c])])
    tw = TopoWidget(root, topo)
    tw.layout()
    tw.pack(expand=True, fill=tk.BOTH)
    root.after(100, tw.draw)
    root.mainloop()
