import queue

import itertools as itr


def piece_move_iter(piece, topo, tile):
    return movement_iters[piece.shape](piece, topo, tile)


class Piece:
    def __init__(self, shape, owner):
        self.shape = shape
        self.owner = owner


def create_move(a, b):
    def f(state):
        b.piece = a.piece
        a.piece = None

    return f


def create_turn():
    def f(state):
        state.turn += 1

    return f


def create_moved(piece):
    def f(state):
        piece.moved = state.turn

    return f


def create_passant(pawn, turn):
    def f(state):
        pawn.passant = turn

    return f


def create_take(b):
    def f(state):
        b.piece = None

    return f


def create_normal_move(a, b, piece):
    return append_move(create_move(a, b), append_move(create_moved(piece), create_turn()))


def append_move(move1, move2):
    def f(state):
        move1(state)
        move2(state)

    return f


def king_move_iter(piece, topo, tile):
    for neigh in tile.neighs:
        yield neigh, create_normal_move(tile, neigh, piece)


def king_move_iter2(piece, topo, tile):
    for b, f in itr.chain(king_move_iter(piece, topo, tile), castle_iter(piece, topo, tile)):
        if all(c.owner == piece.owner for c in b.checks):
            yield b, f


def queen_move_iter(piece, topo, tile):
    q = queue.Queue()

    for neigh in tile.neighs:
        q.put((neigh, neigh.neighs[tile]))

    while not q.empty():
        tile2, vec_in = q.get()

        yield tile2, create_normal_move(tile, tile2, piece)

        if tile2.piece:
            continue

        for neigh, vec_out in tile2.neighs.items():
            if topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile2]))


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
        tile2, vec_in = q.get()

        yield tile2, create_normal_move(tile, tile2, piece)

        if tile2.piece:
            continue

        for neigh, vec_out in tile2.neighs.items():
            if angles(vec_out) and topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile2]))


def bishop_move_iter(piece, topo, tile):
    q = queue.Queue()

    def angles(vec_out):
        return topo.is_angle(vec_out, [1, 0], 1 / 8) \
               or topo.is_angle(vec_out, [1, 0], 3 / 8)

    for neigh, vec_out in tile.neighs.items():
        if angles(vec_out):
            q.put((neigh, neigh.neighs[tile]))

    while not q.empty():
        tile2, vec_in = q.get()

        yield tile2, create_normal_move(tile, tile2, piece)

        if tile2.piece:
            continue

        for neigh, vec_out in tile2.neighs.items():
            if angles(vec_out) and topo.is_angle(vec_in, vec_out, 0.5):
                q.put((neigh, neigh.neighs[tile2]))


def knight_move_iter(piece, topo, tile):
    def angles(vec_out):
        return topo.is_angle(vec_out, [1, 0], 0)\
            or topo.is_angle(vec_out, [1, 0], 0.25)\
            or topo.is_angle(vec_out, [1, 0], 0.5)

    for step1, vec_out in tile.neighs.items():
        if not angles(vec_out):
            continue

        vec_in1 = step1.neighs[tile]

        for step2, vec_out1 in step1.neighs.items():
            if not topo.is_angle(vec_in1, vec_out1, 0.5):
                continue

            vec_in2 = step2.neighs[step1]

            for end, vec_out2 in step2.neighs.items():
                if topo.is_angle(vec_in2, vec_out2, 0.25):
                    yield end, create_normal_move(tile, end, piece)


def pawn_move_iter(piece, topo, tile):
    for neigh, vec in tile.neighs.items():
        m = 1 if piece.owner == 0 else -1

        if topo.is_angle(vec, [0, m], 0.0) and not neigh.piece:
            yield neigh, create_normal_move(tile, neigh, piece)
        elif 0 < topo.angle(vec, [0, m]) / topo.circle < 0.25 and neigh.piece:
            yield neigh, create_normal_move(tile, neigh, piece)


def pawn_move_iter2(piece, topo, tile):
    for neigh, vec in tile.neighs.items():
        m = 1 if piece.owner == 0 else -1

        if topo.is_angle(vec, [0, m], 0.0) and not neigh.piece:
            yield neigh, create_normal_move(tile, neigh, piece)

            if not piece.moved:
                vec_in = neigh.neighs[tile]

                for neigh2, vec_out in neigh.neighs.items():
                    if topo.is_angle(vec_in, vec_out, 0.5):
                        yield neigh2, append_move(create_normal_move(tile, neigh2, piece), create_passant(piece, topo.state.turn))
        elif 0 < topo.angle(vec, [0, m]) / topo.circle < 0.25 and neigh.piece:
            yield neigh, create_normal_move(tile, neigh, piece)


def castle_iter(king, topo, tile):
    r = 10

    if king.moved:
        return

    if not all(c.owner == king.owner for c in tile.checks):
        return

    for neigh1 in tile.neighs:
        vec_in = neigh1.neighs[tile]

        if not all(c.owner == king.owner for c in neigh1.checks):
            continue

        for neigh2, vec_out in neigh1.neighs.items():
            if topo.is_angle(vec_in, vec_out, 0.5):
                curr = neigh2
                vec_in = curr.neighs[neigh1]

                for i in range(r):
                    target = curr.piece

                    if target:
                        if target.shape == "R" and target.owner == king.owner and not target.moved:
                            yield neigh2, append_move(create_normal_move(tile, neigh2, king),
                                                      create_normal_move(curr, neigh1, target))

                        break
                    else:
                        for nxt, vec_out in curr.neighs.items():
                            if topo.is_angle(vec_in, vec_out, 0.5):
                                vec_in = nxt.neighs[curr]
                                curr = nxt
                                break


def en_passant_iter(pawn, topo, tile):
    m1 = 1 if pawn.owner == 0 else -1

    for neigh1, vec_out1 in tile.neighs.items():
        pawn2 = neigh1.piece

        if 0 < topo.angle(vec_out1, [0, m1]) / topo.circle <= 0.25 and pawn2:
            if not pawn2.shape == "p":
                continue

            if not pawn2.passant:
                continue

            if not pawn2.passant == topo.state.turn - 1:
                continue

            m2 = 1 if pawn2.owner == 0 else -1

            for neigh2, vec_out2 in neigh1.neighs.items():
                if topo.is_angle(vec_out2, [0, -m2], 0.0):
                    if neigh2 in tile.neighs and not neigh2.piece:
                        yield neigh2, append_move(create_normal_move(tile, neigh2, pawn), create_take(neigh1))


def pawn_move_iter3(pawn, topo, tile):
    return itr.chain(pawn_move_iter2(pawn, topo, tile), en_passant_iter(pawn, topo, tile))


movement_iters = {"K": king_move_iter2, "Q": queen_move_iter, "R": rook_move_iter, "B": bishop_move_iter,
                  "k": knight_move_iter, "p": pawn_move_iter3}


def set_moved(piece):
    piece.moved = False


def set_en_passant(pawn):
    pawn.passant = False


piece_setups = {"all": set_moved, "p": set_en_passant}


def create_piece(shape, colour):
    piece = Piece(shape, colour)

    piece_setups["all"](piece)

    if shape in piece_setups:
        piece_setups[shape](piece)

    return piece
