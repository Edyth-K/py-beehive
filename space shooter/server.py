import socket
import threading
import time
import struct

local_host = '127.0.0.1'
local_network = '0.0.0.0'

class Server:
    def __init__(self, host=local_network, port=9999):
        self.host = host
        self.port = port

        self.kill = False
        self.thread_count = 0

        self.players = []
        self.player_positions = {}
    
    def run_player_listener(self, conn):
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        with conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if len(data):
                        x, y = struct.unpack('ff', data)
                        self.player_positions[conn] = (x, y)
                except socket.timeout:
                    pass
                except (ConnectionAbortedError, ConnectionResetError):
                    break
        self.thread_count -= 1

    # listener for connections that runs on its own thread
    def connection_listen_loop(self):

        self.thread_count += 1

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # TCP socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True) # optional: easier to reuse address
            s.bind((self.host, self.port)) # listener
            
            while not self.kill:
                s.settimeout(1) # prevents getting stuck in a socket call when trying to stop thread
                s.listen()
                print(f"Server is listening on port {self.port}...")
                try:
                    conn, addr = s.accept()
                    print("New Connection: ", conn, addr)
                    if len(self.players) < 4:
                        self.players.append(conn)
                        self.player_positions[conn] = (0,0)
                        threading.Thread(target=self.run_player_listener, args=(conn,)).start()
                except socket.timeout:
                    # when no one connects, just move on
                    continue
                time.sleep(0.1)
        self.thread_count -= 1
    
    def await_kill(self):
        self.kill = True
        while self.thread_count:
            time.sleep(0.01)
        print("Killed Server")
        
    def run(self):
        threading.Thread(target=self.connection_listen_loop).start()
        try:
            while True:
                print(self.players)
                print(self.player_positions)
                # server action here

                for conn, _ in self.player_positions.items():
                    for other_conn, position in self.player_positions.items():
                        if conn != other_conn:
                            try:
                                conn.send(struct.pack(struct.pack('ff', position[0], position[1])))
                            except OSError:
                                pass
                time.sleep(1)
        except KeyboardInterrupt:
            self.await_kill()

Server().run()