import socket

from core import get_turn
from ui import put_two, interrupt_game, set_interrupt_handler


def make_socket(remote_address, remote_port, local_port=None):
    if not local_port:
        local_port = remote_port

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', local_port))
    s.connect((remote_address, remote_port))

    return s


def make_online(game, local_player, remote, rport, lport=None):
    game.socket = make_socket(remote, rport, lport)

    game.local_player = local_player

    set_interrupt_handler(game, online_interrupt_handler)

    def shutdown():
        game.socket.shutdown(0)
        game.socket.close()
        game.running = False
        interrupt_game(game, ("exit", 0))

    game.shutdown = shutdown

    game.thread_targets += [socket_thread(game, game.socket)]


def online_interrupt_handler(game):
    if game.interrupt[0] == "click":
        if get_turn(game.chess_state) == game.local_player:
            click = game.interrupt[1]

            put_two(game.ibuf, click)

            tile_index = next(i for i, x in enumerate(game.topo.tiles) if x == click)

            game.socket.send(f"{tile_index}".encode())
    elif game.interrupt[0] == "socket":
        if get_turn(game.chess_state) != game.local_player:
            tile_index = game.interrupt[1]

            click = game.topo.tiles[tile_index]

            put_two(game.ibuf, click)


def socket_thread(game, s):
    def f():
        data = True

        try:
            while game.running and data:
                data = int(s.recv(1024).decode())

                interrupt_game(game, ("socket", data))
        except ConnectionError:
            ...

    return f
