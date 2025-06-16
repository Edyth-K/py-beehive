from settings import *
import time
from player import Player

class Game:
    def __init__(self):
        
        pygame.init()

        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor-like")
        self.running = True
        self.clock = pygame.time.Clock()

        self.all_sprites = pygame.sprite.Group()
        self.player = Player(self.all_sprites, (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))

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