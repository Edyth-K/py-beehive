import pygame
from os.path import join
from random import randint
import time
import struct
import threading
import socket

class Client:
    def __init__(self, host='192.168.4.148', port=9999):
        
        # netcode
        self.is_connected = False

        self.host = host
        self.port = port

        self.kill = False
        self.socket = None

        # general setup
        pygame.init()
        WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
        WINDOW_DIMENSIONS = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.display_surface = pygame.display.set_mode(WINDOW_DIMENSIONS)
        pygame.display.set_caption("Change")
        self.running = True
        self.clock = pygame.time.Clock()


        # surface
        self.surf = pygame.Surface((100, 200))
        self.x = 100
        self.y = 100

        self.bg_surf = pygame.image.load(join('resources', 'images', 'bg.jpg')).convert()
        self.bg_surf = pygame.transform.scale(self.bg_surf, self.display_surface.get_size())
        self.bg_rect = self.bg_surf.get_frect(topleft = (0,0))

        # importing images
        self.player_surf = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        self.player_rect = self.player_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT-WINDOW_HEIGHT/4))
        self.drag_player = False # boolean to see if cursor is pressed on player
        self.player_speed = 500
        self.player_direction = pygame.math.Vector2(0,0)

        self.player2_surf = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        self.player2_rect = self.player2_surf.get_frect(center = (-100,WINDOW_HEIGHT-100))

        # star_surf = pygame.image.load(join('space shooter', 'resources', 'images', 'star.png')).convert_alpha()
        # star_pos = []
        # for i in range(20):
        #     star_pos.append(((randint(0,1200)), (randint(0,650))))

        self.meteor_surf = pygame.image.load(join('resources', 'images', 'meteor.png')).convert_alpha()
        self.meteor_rect = self.meteor_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

        self.laser_surf = pygame.image.load(join('resources', 'images', 'laser.png')).convert_alpha()
        self.laser_rect = self.laser_surf.get_frect(bottomleft = (20,WINDOW_HEIGHT-20))


    def run_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.connect((self.host, self.port))
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            s.settimeout(1)
            print("Connected: ", s)
            self.is_connected = True
            self.socket = s
            while not self.kill:
                try:
                    data = self.socket.recv(4096)
                    if len(data):
                        update_format = 'ff'
                        if len(data) >= struct.calcsize(update_format):
                            self.player2_rect.topleft = struct.unpack_from(update_format, data, 0)
                except socket.timeout:
                    pass
                time.sleep(0.001)

    def run(self):
        threading.Thread(target=self.run_listener).start()
        while self.running:

            dt = self.clock.tick(120) / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.kill = True
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.player_rect.collidepoint(pygame.mouse.get_pos()):
                        self.drag_player = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.drag_player = False
                if event.type == pygame.MOUSEMOTION:
                    if self.drag_player:
                        self.player_rect.center = pygame.mouse.get_pos()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player_direction.y = -1
            else:
                self.player_direction.y = 0
            if keys[pygame.K_a]:
                self.player_direction.x = -1
            else:
                self.player_direction.x = 0
            if keys[pygame.K_s]:
                self.player_direction.y = 1
            if keys[pygame.K_d]:
                self.player_direction.x = 1


            self.player_direction = self.player_direction.normalize() if self.player_direction else self.player_direction
            self.player_rect.center += self.player_direction * self.player_speed * dt

            # draw
            self.display_surface.fill((30, 30, 30))
            self.display_surface.blit(self.bg_surf, self.bg_rect)


            # draw stars
            # for i in range(20):
            #     display_surface.blit(star_surf, star_pos[i])

            self.display_surface.blit(self.meteor_surf, self.meteor_rect)
            self.display_surface.blit(self.laser_surf, self.laser_rect)

            
            self.display_surface.blit(self.player2_surf, self.player2_rect)
            self.display_surface.blit(self.player_surf, self.player_rect)
        
            print(self.player_rect.x+self.player_rect.width/2)
            pygame.display.update()

            if self.is_connected:
                try:
                    self.socket.sendall(struct.pack('ff', self.player_rect.x, self.player_rect.y))
                except (AttributeError, OSError):
                    pass
            
            time.sleep(0.001)

        pygame.quit()

Client().run()