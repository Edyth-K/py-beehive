import pygame
from os.path import join
from random import randint, random
import time
import struct
import threading
import socket

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
laser_sprites = pygame.sprite.Group()

class Player(pygame.sprite.Sprite):
    def __init__(self, groups,  pos=(WINDOW_WIDTH/2, WINDOW_HEIGHT-WINDOW_HEIGHT/4)):
        super().__init__(groups)
        self.image = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.drag = False # boolean to see if cursor is pressed on player
        self.speed = 500
        self.direction = pygame.math.Vector2(0,0)

        # laser 
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        self.group = groups
        self.laser_surf = pygame.image.load(join('resources', 'images', 'laser.png')).convert_alpha()
        self.laser_sound = pygame.mixer.Sound(join('resources', 'audio', 'laser.wav'))
        # mask
        self.mask = pygame.mask.from_surface(self.image)
        # self.mask_surf = self.mask.to_surface() 
        # self.mask_surf.set_colorkey((0,0,0))
        # self.image = self.mask_surf

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time > self.cooldown_duration:
                self.can_shoot = True


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
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser((self.group, laser_sprites), self.laser_surf, self.rect.midtop)
            self.laser_sound.play()
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WINDOW_WIDTH), randint(0,WINDOW_HEIGHT)))
    
    def update(self, dt):
        pass

class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos=(20,WINDOW_HEIGHT-20)):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 1000
        

    
    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom <= 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, surf, pos):
        super().__init__(groups)
        self.image = surf
        self.original_surf = surf
        self.rect = self.image.get_frect(midbottom = pos)
        self.speed = 400
        self.direction = pygame.math.Vector2(random()-0.5, 1)
        self.duration = 3000
        self.spawn_time = pygame.time.get_ticks()
        self.rotation = 0
        self.rotation_speed = randint(0,200)

    
    def update(self, dt):
        #self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
        current_time = pygame.time.get_ticks()
        if current_time - self.spawn_time >= self.duration:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        
    
    def update(self, dt):
        self.frame_index += 50 * dt
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]


class Background(pygame.sprite.Sprite):
    def __init__(self, groups, display_surface):
        super().__init__(groups)
        self.image = pygame.image.load(join('resources', 'images', 'bg.jpg')).convert()
        self.image = pygame.transform.scale(self.image, display_surface.get_size())
        self.rect = self.image.get_frect(topleft = (0,0))

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

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Space Shooter")
        self.running = True
        self.clock = pygame.time.Clock()

        # imports
        # star_surf = pygame.image.load(join('resources', 'images', 'star.png')).convert_alpha()
        self.meteor_surf = pygame.image.load(join('resources', 'images', 'meteor.png')).convert_alpha()
        self.font = pygame.font.Font(join('resources', 'images', 'Oxanium-Bold.ttf'), 40) #font, size
        self.explosion_frames = [pygame.image.load(join('resources', 'images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
        self.explosion_sound = pygame.mixer.Sound(join('resources', 'audio', 'explosion.wav'))
        self.bg_music = pygame.mixer.Sound(join('resources', 'audio', 'game_music.wav'))


        # sprites
        self.all_sprites = pygame.sprite.Group()
        self.meteor_sprites = pygame.sprite.Group()
        self.bg = Background(self.all_sprites, self.display_surface)
        # for i in range(20):
        #     Star(self.all_sprites, star_surf)
        self.player = Player(self.all_sprites)

        # MULTIPLAYER (outdated; need to create Player() object for player2)
        # self.player2_surf = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
        # self.player2_rect = self.player2_surf.get_frect(center = (-100,WINDOW_HEIGHT-100))

    def display_score(self):
        current_time = pygame.time.get_ticks()
        self.text_surf = self.font.render(str(int(current_time/100)), True, '#ffffff') # string, anti-alias (bool), color
        self.text_rect = self.text_surf.get_frect(midbottom = (WINDOW_WIDTH/2, WINDOW_HEIGHT-50))
        self.display_surface.blit(self.text_surf, self.text_rect)
        pygame.draw.rect(self.display_surface, 'white', self.text_rect.inflate(20, 15).move(0,-5), 5, 10)
    
    def check_collisions(self): 
        if (pygame.sprite.spritecollide(self.player, self.meteor_sprites, False, pygame.sprite.collide_mask)):
            self.running = False

        for laser in laser_sprites:
            if (pygame.sprite.spritecollide(laser, self.meteor_sprites, True)):
                laser.kill()
                AnimatedExplosion(self.explosion_frames, laser.rect.midtop, self.all_sprites)
                self.explosion_sound.play()

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

        # custom event -> meteor event
        meteor_event = pygame.event.custom_type()
        pygame.time.set_timer(meteor_event, 500)

        self.bg_music.set_volume(0.2)
        self.bg_music.play(loops=-1) # -1: loop indefinitely

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
                if event.type == meteor_event:
                    Meteor((self.all_sprites, self.meteor_sprites), self.meteor_surf, (randint(0,WINDOW_WIDTH), 0))

            # update sprites
            self.all_sprites.update(dt)

            # check collisions
            self.check_collisions()

            # draw sprites
            
            self.all_sprites.draw(self.display_surface)
            self.display_score()
             
            # MULTIPLAYER (outdated; need to create Player object for player2)
            # self.display_surface.blit(self.player2_surf, self.player2_rect)
            
            # if self.is_connected:
            #     try:
            #         self.socket.sendall(struct.pack('ff', self.player_rect.x, self.player_rect.y))
            #     except (AttributeError, OSError):
            #         pass



            pygame.display.update()

            time.sleep(0.001)

        pygame.quit()

Client().run()