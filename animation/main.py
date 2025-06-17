import pygame

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, pos, frame_speed=10):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = self.frames[int(self.index)]
        self.rect = self.image.get_frect(topleft=pos)
        self.frame_speed = frame_speed
        self.timer = 0

    def update(self, dt):
        self.index += self.frame_speed * dt
        if self.index >= len(self.frames):
            self.index = 0
        self.image = self.frames[int(self.index)]

class AnimationManager():
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Animation Test")
        self.clock = pygame.time.Clock()
        self.running = True

        self.spritesheet = pygame.image.load('sheet.png').convert()
        self.spritesheet.set_colorkey((255, 0, 255))  # Magenta background

        fw = 32
        self.animations = {
            "idle": [pygame.Rect(4*fw + i * fw, 0, fw, fw) for i in range(4)],
            "run_left": [pygame.Rect(4*fw + i * fw, fw*2, fw, fw) for i in range(4)],
            "run_right": [pygame.Rect(4*fw + i * fw, fw*3, fw, fw) for i in range(4)],
            "run_down": [pygame.Rect(4*fw + i * fw, fw*4, fw, fw) for i in range(4)],
            "run_up": [pygame.Rect(4*fw + i * fw, fw*5, fw, fw) for i in range(4)],
            "run_downleft": [pygame.Rect(4*fw + i * fw, fw*6, fw, fw) for i in range(4)],
            "run_downright": [pygame.Rect(4*fw + i * fw, fw*7, fw, fw) for i in range(4)],
            "run_upleft": [pygame.Rect(4*fw + i * fw, fw*8, fw, fw) for i in range(4)],
            "run_upright": [pygame.Rect(4*fw + i * fw, fw*9, fw, fw) for i in range(4)]
        }

        idle_frames = self.extract_animation_frames(self.spritesheet, self.animations["run_downright"])

        self.player = AnimatedSprite(idle_frames, pos=(300, 200), frame_speed=10)
        self.all_sprites = pygame.sprite.Group(self.player)

    def extract_animation_frames(self, sheet, frame_rects, scale=5):
        frames = []
        for rect in frame_rects:
            frame = sheet.subsurface(rect).copy()
            new_size = (int(rect.width * scale), int(rect.height * scale))
            frame = pygame.transform.scale(frame, new_size)
            frames.append(frame)
        return frames

    def run(self):

        previous_anim = None
        while self.running:
            dt = self.clock.tick(120) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()
            direction = pygame.Vector2(0, 0)
            if keys[pygame.K_w]:
                direction.y = -1
            if keys[pygame.K_s]:
                direction.y = 1
            if keys[pygame.K_a]:
                direction.x = -1
            if keys[pygame.K_d]:
                direction.x = 1
            self.player.rect.center += direction * 300 * dt
            print(self.player.rect.center)
            
            current_anim = "idle"
            if direction.length_squared() > 0:
                if direction.y > 0:
                    if direction.x > 0:
                        current_anim = "run_downright"
                    elif direction.x < 0:
                        current_anim = "run_downleft"
                    else:
                        current_anim = "run_down"
                elif direction.y < 0:
                    if direction.x > 0:
                        current_anim = "run_upright"
                    elif direction.x < 0:
                        current_anim = "run_upleft"
                    else:
                        current_anim = "run_up"
                else:
                    if direction.x > 0:
                        current_anim = "run_right"
                    elif direction.x < 0:
                        current_anim = "run_left"

            if current_anim != previous_anim:
                frames = self.extract_animation_frames(self.spritesheet, self.animations[current_anim], scale=5)
                frame_index = 0
                previous_anim = current_anim

            frame_index += 10 * dt
            if frame_index >= len(frames):
                frame_index = 0

            self.display_surface.fill((230, 230, 230))
            self.display_surface.blit(frames[int(frame_index)], (self.player.rect.center))
            pygame.display.flip()

        pygame.quit()

AnimationManager().run()

