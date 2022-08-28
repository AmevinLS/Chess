import pygame
import chess
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    QUIT,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN
)


def convert_coords(x, y):
    letter = chr(ord("a") + y)
    number = str(8 - x)
    return letter + number


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg = pygame.image.load("resources/board.png")
game = chess.Game()

running = True
while running:
    screen.blit(bg, (0, 0))

    board = game.get_board()
    for i in range(8):
        for j in range(8):
            kind_str = board[i][j].kind.value
            color_str = board[i][j].color.value
            if kind_str == "empty":
                continue
            piece_im = pygame.image.load(f"resources/{color_str}_{kind_str}.png")
            screen.blit(piece_im, (100*j, 100*i))

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            x_pos, y_pos = pygame.mouse.get_pos()
            from_sqr = convert_coords(y_pos//100, x_pos//100)
        elif event.type == MOUSEBUTTONUP:
            x_pos, y_pos = pygame.mouse.get_pos()
            to_sqr = convert_coords(y_pos//100, x_pos//100)
            move = f"{from_sqr}-{to_sqr}"
            game.make_move(move)
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
    pygame.display.update()

print(";".join(game.get_history()))
