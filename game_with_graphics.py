import pygame
import os
from pygame.locals import KEYDOWN, K_ESCAPE, QUIT

pygame.init()

SCREEN_WIDTH = 800

SCREEN_HEIGHT = 800

bg = pygame.image.load(os.path.join("resources", "board.png"))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = True

while running:
    screen.blit(bg, (0, 0))
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
