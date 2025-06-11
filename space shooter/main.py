import pygame
from os.path import join
from random import randint

# general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
WINDOW_DIMENSIONS = (WINDOW_WIDTH, WINDOW_HEIGHT)
display_surface = pygame.display.set_mode(WINDOW_DIMENSIONS)
pygame.display.set_caption("Change")
running = True

#surface
surf = pygame.Surface((100, 200))
x = 100
y = 100
surf.fill('orange')

# importing an image
player_surf = pygame.image.load(join('resources', 'images', 'player.png')).convert_alpha()
player_rect = player_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
# boolean to see if cursor is pressed on player
drag_player = False

star_surf = pygame.image.load(join('resources', 'images', 'star.png')).convert_alpha()
star_pos = []
for i in range(20):
    star_pos.append(((randint(0,1200)), (randint(0,650))))


while running:
    
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player_rect.collidepoint(pygame.mouse.get_pos()):
                print(event)
                drag_player = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drag_player = False

    # update
    # print(pygame.mouse.get_pressed()[0])
    # print(pygame.mouse.get_pos())


    # draw
    display_surface.fill('darkgray')

    
    for i in range(20):
        display_surface.blit(star_surf, star_pos[i])
    if drag_player:
        player_rect.center = pygame.mouse.get_pos()
    display_surface.blit(player_surf, player_rect)
    
    pygame.display.update()

pygame.quit()
