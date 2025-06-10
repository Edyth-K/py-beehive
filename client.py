import pygame
import sys
import socket
import threading
import time
import struct

class Client:
    def __init__(self, host='127.0.0.1', port=9999):

        self.host = host
        self.port = port

        self.kill = False
        self.socket = None

        # Initialize Pygame
        pygame.init()

        # Window dimensions
        self.screen = pygame.display.set_mode((800, 850))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Move the Red Square")
        self.font = pygame.font.Font(size=34)

        self.x, self.y = 100, 100
        self.speed = 5
        self.size = 50

    def update(self):
        self.screen.fill((30, 30, 30))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.kill = True
                pygame.quit()
                sys.exit()

        # Draw the red square
        pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, self.size, self.size))
        pygame.display.update()

    def send_to_server(self):
        self.socket.sendall(struct.pack('ii', self.x, self.y))

    def run_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            s.settimeout(1)
            print("Connected: ", s)
            self.socket = s
            while not self.kill:
                try:
                    data = self.socket.recv(4096)
                    if len(data):
                        pass
                except socket.timeout:
                    pass
                time.sleep(0.001)

    def run(self):
        threading.Thread(target=self.run_listener).start()
        while True:
            self.clock.tick(60) 
            self.update()
            # Key press detection
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]: self.y -= self.speed
            if keys[pygame.K_s]: self.y += self.speed
            if keys[pygame.K_a]: self.x -= self.speed
            if keys[pygame.K_d]: self.x += self.speed
            self.send_to_server()
            time.sleep(0.001)

Client().run()