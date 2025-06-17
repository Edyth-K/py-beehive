from settings import *
import time
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint

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

        # map
        self.setup()

        # sprites
        # player_spawn = (2000,2000)#(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        # self.player = Player(player_spawn, self.all_sprites, self.collision_sprites) # moved to setup()


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

    def run(self):
        while self.running:
            dt = self.clock.tick(120) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
        
            # update
            self.all_sprites.update(dt)

            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            

            pygame.display.update()

            time.sleep(0.001)

        pygame.quit()

if __name__ == '__main__':
    Game().run()