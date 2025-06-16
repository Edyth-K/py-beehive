from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(join('assets', 'images', 'player','sheet.png')).convert_alpha()
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.animation_speed = 5
        
        self.rect = self.frames['idle'][0].get_frect(center = pos)

        self.hitbox_rect = self.rect.inflate(-100, -100) # shrink width of hitbox by 40
        self.speed = 500
        self.direction = pygame.math.Vector2(0,0)
        self.collision_sprites = collision_sprites

    def load_images(self):
        # LOAD FRAMES FROM SINGLE SPRITE SHEET
        self.frames = {'idle': [], 'left':[], 'right':[], 'up':[], 'down':[],
                       'attack':[],'d_left':[],'d_right':[],'u_left':[],'u_right':[]}
        state_index = -1
        scale = 4
        for state in self.frames.keys():
            state_index += 1
            for frame_index in range(4):
                rect = pygame.Rect(frame_index*32, state_index*32, 32, 32)
                frame = self.image.subsurface(rect).copy()
                new_size = (int(rect.width * scale), int(rect.height * scale))
                frame = pygame.transform.scale(frame, new_size)
                self.frames[state].append(frame)


        # LOAD FRAMES FROM MULTIPLE IMAGES
        # self.frames = {'left':[], 'right':[], 'up':[], 'down':[]}

        # for state in self.frames.keys():
        #     for folder_path, sub_folders, file_names in walk(join('assets', 'images', 'player', state)):
        #         if file_names:
        #             for file_name in sorted(file_names, key= lambda name: int(name.split('.')[0])):
        #                 full_path = join(folder_path, file_name)
        #                 surf = pygame.image.load(full_path).convert_alpha()
        #                 self.frames[state].append(surf)
        

    def animate(self, dt):

        # 8-direction movement key
        DIRECTION_TO_ANIM = {
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right",
            (-1, -1): "u_left",
            (1, -1): "u_right",
            (-1, 1): "d_left",
            (1, 1): "d_right",
            (0, 0): "idle"
        }
        
        # get state
        self.state = DIRECTION_TO_ANIM[(round(self.direction.x), round(self.direction.y))]
        # if self.direction.x != 0:
        #     self.state = 'right' if self.direction.x > 0 else 'left'
        # if self.direction.y != 0:
        #     self.state = 'down' if self.direction.y > 0 else 'up'
        # if self.direction.x == 0 and self.direction.y == 0:
        #     self.state = 'idle'

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


    