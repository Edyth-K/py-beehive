from settings import *
import time
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame

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
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # map
        self.setup()

        # sprites
        self.player = Player((WINDOW_WIDTH/2, WINDOW_HEIGHT/2), self.all_sprites, self.collision_sprites)


    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))


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
            self.all_sprites.draw(self.display_surface)

            pygame.display.update()

            time.sleep(0.001)

        pygame.quit()

if __name__ == '__main__':
    Game().run()