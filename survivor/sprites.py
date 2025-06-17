from settings import *
from math import atan2, degrees

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.ground = True

class AimIndicator(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        # player connection
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(0,1) # direction from gun -> player

        # sprite setup
        super().__init__(groups)
        self.aim_surf = pygame.image.load(join('assets', 'images', 'gun', 'gun.png')).convert_alpha()
        self.image = self.aim_surf
        self.rect = self.image.get_frect(center = self.player.rect.center + self.player_direction * self.distance)

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        direction = mouse_pos - player_pos
        if direction.magnitude() > 0:
            self.player_direction = direction.normalize() 

    def rotate_aim(self):
        angle_radians = atan2(self.player_direction.x, self.player_direction.y)
        angle = degrees(angle_radians) - 90
        if self.player_direction.x >= 0:
            self.image = pygame.transform.rotozoom(self.aim_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.aim_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_aim()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

