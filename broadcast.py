import socket
import select
import threading
import traceback

server_port = 50002

rooms = {}
threads = {}

def mainloop():
    print(f"Opening server on {server_port}...")
    s = socket.socket()
    s.bind(('', server_port))  # port forward this
    s.listen(128)

    print("Opened server")
    
    while True:
        print("Waiting for requests...")
        c1, a1 = s.accept()
        print(f"Incoming connection from {a1}")

        room = c1.recv(1024).decode()

        print("Received subscription")
        process((c1, a1), room)


def broadcast(sockets):
    try:
        while sockets:
            r, _, _ = select.select(sockets, [], [])
            r = r[0]

            msg = r.recv(1024)

            if not msg:
                r.shutdown(0)
                r.close()
                sockets.remove(r)

            for s in sockets:
                if s == r:
                    continue

                s.send(msg)
    except Exception as e:
        traceback.print_exc()


def process(addr1, room):
    c1, a1 = addr1

    print(f"Client wants to connect to room {room}")

    rooms.setdefault(room, []).append(c1)

    if room in threads:
        print("Room was open.")
    else:
        thread = threading.Thread(target=lambda: broadcast(rooms[room]))
        threads[room] = thread
        thread.start()
        print("Opened room")

mainloop()
