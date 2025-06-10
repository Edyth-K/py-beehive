import socket
import threading
import time
import struct

class Server:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port

        self.kill = False
        self.thread_count = 0

        self.players = []
    
    def run_player_listener(self, conn):
        self.thread_count += 1
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        conn.settimeout(1)
        with conn:
            while not self.kill:
                try:
                    data = conn.recv(4096)
                    if len(data):
                        x, y = struct.unpack('ii', data)
                        print(f"Received: {x}, {y}")
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
                try:
                    conn, addr = s.accept()
                    print("New Connection: ", conn, addr)
                    if len(self.players) < 4:
                        self.players.append(conn)
                        threading.Thread(target=self.run_player_listener, args=(conn,)).start()
                except socket.timeout:
                    # when no one connects, just move on
                    continue
                time.sleep(0.01)


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
                # server action here

                # for player_conn in self.players:
                #     try:
                #         player_conn.send(self.serialize())
                #     except OSError:
                #         pass
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.await_kill()

Server().run()