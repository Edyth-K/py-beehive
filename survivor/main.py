from settings import *
import time
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor-like")
        self.running = True
        self.clock = pygame.time.Clock()

        # groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()

        # weapon timer
        self.can_attack = True
        self.attack_time = 0
        self.attack_cooldown = 100

        # enemy spawn timer
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []

        # audio
        self.attack_sound = pygame.mixer.Sound(join('assets', 'audio', 'shoot.wav'))
        self.attack_sound.set_volume(0.4)
        self.hit_sound = pygame.mixer.Sound(join('assets', 'audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('assets', 'audio', 'music.wav'))
        self.music.set_volume(0.3)
        self.music.play(loops = -1)

        # load images and map
        self.load_images()
        self.setup()

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_attack:
            self.attack_sound.play()
            pos = self.aim_indicator.rect.center +  self.aim_indicator.player_direction * 50
            Bullet(self.bullet_surf, pos, self.aim_indicator.player_direction, (self.all_sprites, self.attack_sprites))
            self.can_attack = False
            self.attack_time = pygame.time.get_ticks()

    def attack_timer(self):
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

    def load_images(self):
        self.bullet_surf = pygame.image.load(join('assets', 'images', 'gun', 'bullet.png')).convert_alpha()
        folders = list(walk(join('assets', 'images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('assets', 'images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key = lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        # ground layer
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        # collision layer (for ground tiles)
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), (self.collision_sprites))

        # object layer
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.aim_indicator = AimIndicator(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def attack_collision(self):
        if self.attack_sprites:
            for attack in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.hit_sound.play()
                    for sprite in collision_sprites:
                        sprite.destroy() 
                    attack.kill()

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False):
            self.running = False
        

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
        
            # update
            self.attack_timer()
            self.input()
            self.all_sprites.update(dt)
            self.attack_collision()
            self.player_collision()

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            

            pygame.display.update()

            time.sleep(0.001)

        pygame.quit()

if __name__ == '__main__':
    Game().run()