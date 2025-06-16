from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.animation_speed = 5
        self.image = pygame.image.load(join('assets', 'images', 'player','down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(-100, -100) # shrink width of hitbox by 40
        self.speed = 500
        self.direction = pygame.math.Vector2(0,0)
        self.collision_sprites = collision_sprites

    def load_images(self):
        self.frames = {'left':[], 'right':[], 'up':[], 'down':[]}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('assets', 'images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)
        print(self.frames)

    def animate(self, dt):
        # get state
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        if self.direction.x == 0 and self.direction.y == 0:
            self.frame_index = 0

        # animate
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def input(self):
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

    def move(self, dt):
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

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)


    