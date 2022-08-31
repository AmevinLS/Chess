import pygame
import chess_bots
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
shade = pygame.image.load("resources/shade.png")
game = chess.Game()
bot = chess_bots.RandomBot()

running = True
checkmate = False
cm_x_pos = cm_y_pos = 0
while running:
    # Drawing the background
    screen.blit(bg, (0, 0))

    if checkmate:
        pygame.draw.rect(
            screen, (255, 0, 0),
            pygame.Rect(cm_x_pos, cm_y_pos, 100, 100)
        )

    # Drawing the shade
    mouse_x, mouse_y = pygame.mouse.get_pos()
    x = mouse_x // 100 * 100
    y = mouse_y // 100 * 100
    screen.blit(shade, (x, y))

    # Drawing the board
    board = game.get_board()
    for i in range(8):
        for j in range(8):
            kind_str = board[i][j].kind.value
            color_str = board[i][j].color.value
            if kind_str == "empty":
                continue
            piece_im = pygame.image.load(f"resources/{color_str}_{kind_str}.png")
            screen.blit(piece_im, (100*j, 100*i))

    # Processing events
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            x_pos, y_pos = pygame.mouse.get_pos()
            from_sqr = convert_coords(y_pos//100, x_pos//100)
        elif event.type == MOUSEBUTTONUP:
            x_pos, y_pos = pygame.mouse.get_pos()
            to_sqr = convert_coords(y_pos//100, x_pos//100)
            move = f"{from_sqr}-{to_sqr}"
            game.play_move(move)

            cond = game.get_condition()
            state = game.get_state()

            move = bot.get_move(state)
            game.play_move(move)

            color = state.color_to_move
            if cond == chess.State.Condition.CHECKMATE:
                checkmate = True
                i, j = state._find_king(color)
                cm_x_pos, cm_y_pos = j * 100, i * 100

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
    pygame.display.update()

print(";".join(game.get_history()))
