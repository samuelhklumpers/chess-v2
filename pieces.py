import queue


def piece_move_iter(piece, topo, tile):
    return movement_iters[piece.shape](piece, topo, tile)


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
                    yield end


def pawn_move_iter(piece, topo, tile):
    for neigh, vec in tile.neighs.items():
        m = 1 if piece.owner == 0 else -1

        if topo.is_angle(vec, [0, m], 0.0) and not neigh.piece:
            yield neigh
        elif 0 < topo.angle(vec, [0, m]) / topo.circle < 0.25 and neigh.piece:
            yield neigh


def pawn_move_iter2(piece, topo, tile):
    for neigh, vec in tile.neighs.items():
        m = 1 if piece.owner == 0 else -1

        if topo.is_angle(vec, [0, m], 0.0) and not neigh.piece:
            yield neigh

            if not piece.moved:
                vec_in = neigh.neighs[tile]

                for neigh2, vec_out in neigh.neighs.items():
                    if topo.is_angle(vec_in, vec_out, 0.5):
                        yield neigh2
        elif 0 < topo.angle(vec, [0, m]) / topo.circle < 0.25 and neigh.piece:
            yield neigh


def castle_iter(king, topo, tile):
    ...  # select tiles at 2 distance, then filter by repeating the path to that tile until a rook is found or not


movement_iters = {"K": king_move_iter, "Q": queen_move_iter, "R": rook_move_iter, "B": bishop_move_iter,
                  "k": knight_move_iter, "p": pawn_move_iter2}


def set_moved(piece):
    piece.moved = False


def set_en_passant(pawn):
    pawn.passant = False


piece_setups = {"all": set_moved}


def create_piece(shape, colour):
    piece = Piece(shape, colour)

    piece_setups["all"](piece)

    if shape in piece_setups:
        piece_setups[shape](piece)

    return piece
