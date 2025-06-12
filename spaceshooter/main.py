import pygame
from os.path import join
from random import randint
import time
import struct
import threading
import socket

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WINDOW_DIMENSIONS = (WINDOW_WIDTH, WINDOW_HEIGHT)

class Player(pygame.sprite.Sprite):
    def __init__(self, groups,  pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT-WINDOW_HEIGHT/4)):
        super().__init__(groups)
        self.image = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.drag = False # boolean to see if cursor is pressed on player
        self.speed = 500
        self.direction = pygame.math.Vector2(0,0)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.direction.y = -1
        else:
            self.direction.y = 0
        if keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if keys[pygame.K_s]:
            self.direction.y = 1
        if keys[pygame.K_d]:
            self.direction.x = 1

        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE]:
            pass # TODO: fire laser

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), randint(0,WINDOW_HEIGHT)))
    
    def update(self, dt):
        pass

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

        self.display_surface = pygame.display.set_mode(WINDOW_DIMENSIONS)
        pygame.display.set_caption("Change")
        self.running = True
        self.clock = pygame.time.Clock()

        # surface
        self.surf = pygame.Surface((100, 200))
        self.x = 100
        self.y = 100

        self.all_sprites = pygame.sprite.Group()
    
        self.bg_surf = pygame.image.load(join('resources', 'images', 'bg.jpg')).convert()
        self.bg_surf = pygame.transform.scale(self.bg_surf, self.display_surface.get_size())
        self.bg_rect = self.bg_surf.get_frect(topleft = (0,0))

        star_surf = pygame.image.load(join('resources', 'images', 'star.png')).convert_alpha()
        for i in range(20):
            Star(self.all_sprites, star_surf)
        self.player = Player(self.all_sprites)

        self.player2_surf = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        self.player2_rect = self.player2_surf.get_frect(center = (-100,WINDOW_HEIGHT-100))

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
        # MULTIPLAYER
        # threading.Thread(target=self.run_listener).start()

        while self.running:

            dt = self.clock.tick(120) / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.kill = True
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.player.rect.collidepoint(pygame.mouse.get_pos()):
                        self.player.drag = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.player.drag = False
                if event.type == pygame.MOUSEMOTION:
                    if self.player.drag:
                        self.player.rect.center = pygame.mouse.get_pos()

            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill((30, 30, 30))
            self.display_surface.blit(self.bg_surf, self.bg_rect)

            self.display_surface.blit(self.meteor_surf, self.meteor_rect)
            self.display_surface.blit(self.laser_surf, self.laser_rect)

            # MULTIPLAYER
            # self.display_surface.blit(self.player2_surf, self.player2_rect)


            self.all_sprites.draw(self.display_surface)

            pygame.display.update()

            if self.is_connected:
                try:
                    self.socket.sendall(struct.pack('ff', self.player_rect.x, self.player_rect.y))
                except (AttributeError, OSError):
                    pass
            
            time.sleep(0.001)

        pygame.quit()

Client().run()