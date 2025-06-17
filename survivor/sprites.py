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
        self.aim_surf = pygame.image.load(join('assets', 'images', 'gun', 'sword.png')).convert_alpha()
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

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.spawn_time = pygame.time.get_ticks()
        self.duration = 2000
        self.direction = direction
        self.speed = 500
        self.animation_speed = 10
        self.frame_index = 0
        
        self.frames = []
        scale = 2
        for frame_index in range(4):
            rect = pygame.Rect(frame_index*32, 0, 32, 32)
            frame = self.image.subsurface(rect).copy()
            new_size = (int(rect.width * scale), int(rect.height * scale))
            frame = pygame.transform.scale(frame, new_size)
            self.frames.append(frame)
        print(self.frames)
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        self.animate(dt)
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites, death_sound):
        super().__init__(groups)
        self.player = player

        # image
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animation_speed = 6

        # rect
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-20,-40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.speed = 200

        self.death_time = 0
        self.death_duration = 200
        self.death_sound = death_sound

    def move(self, dt):
        # get direction
        player_pos = pygame.Vector2(self.player.rect.center) 
        enemy_pos = pygame.Vector2(self.rect.center)
        direction = player_pos - enemy_pos
        if direction != 0:
            self.direction = (direction).normalize()

        # update position + collision logic
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                if direction == 'vertical':
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def destroy(self):
        self.death_time = pygame.time.get_ticks()
        surf = pygame.mask.from_surface(self.frames[0]).to_surface()
        surf.set_colorkey('black')
        self.image = surf


    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.death_sound.play()
            self.kill()

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]

    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else: 
            self.death_timer()