from settings import *

class Player(pygame.sprite.Sprite):

    def __init__(self, groups):
        super().__init__(groups)

        # image
        self.image = pygame.Surface(SIZE['paddle'])

        # rect & movement
        self.rect = self.image.get_frect(center = POS['player'])

class Ball(pygame.sprite.Sprite):
    pass