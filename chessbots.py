import chess
import numpy as np
import time
import threading
from random import shuffle
import pygame
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    QUIT,
    MOUSEBUTTONUP,
    MOUSEBUTTONDOWN
)


class Player:
    def __init__(self):
        self.move_ready = False
        self.move = None

    def is_move_ready(self):
        return self.move_ready

    def get_move(self):
        self.move_ready = False
        move = self.move
        self.move = None
        return move

    def request_move(self, state: chess.State):
        return


class Human(Player):
    def __init__(self):
        super().__init__()
        return

    def _find_move(self, state: chess.State):
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    x_pos, y_pos = pygame.mouse.get_pos()
                    from_coords = [y_pos//100, x_pos//100]
                elif event.type == MOUSEBUTTONUP:
                    x_pos, y_pos = pygame.mouse.get_pos()
                    to_coords = [y_pos//100, x_pos//100]

                    move = from_coords + to_coords
                    if state.is_valid_move(move):
                        self.move = move
                        self.move_ready = True
                        return

    def request_move(self, state: chess.State):
        thr = threading.Thread(target=self._find_move, args=(state,))
        thr.start()
        return


class RandomBot(Player):
    def __init__(self):
        super().__init__()

    def _find_move(self, state: chess.State):
        time.sleep(2)
        poss_moves = state.get_possible_moves()
        ind = np.random.randint(0, len(poss_moves))
        self.move = poss_moves[ind]
        self.move_ready = True
        return

    def request_move(self, state: chess.State):
        thr = threading.Thread(target=self._find_move, args=(state,))
        thr.start()
        return


class MinMaxBot(Player):
    class Node:
        def __init__(self, state: chess.State):
            self.state = state
            self.eval = state.get_imbalance()
            self.childs = []

        def _create_childs(self):
            self.poss_moves = self.state.get_possible_moves()
            shuffle(self.poss_moves)
            for move in self.poss_moves:
                self.childs.append(MinMaxBot.Node(self.state.play_move(move)))

        def build_tree(self, max_depth, depth=0):
            if depth >= max_depth:
                del self.state
                return

            self._create_childs()
            color_to_move = self.state.color_to_move
            del self.state
            for child in self.childs:
                child.build_tree(max_depth, depth+1)
            # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            #     futures = [
            #         executor.submit(child.build_tree, max_depth, depth+1) for child in self.childs
            #     ]
            # concurrent.futures.wait(futures)

            childs_evals = [child.eval for child in self.childs]
            if color_to_move == chess.Color.WHITE:
                ind = np.argmax(childs_evals)
            else:
                ind = np.argmin(childs_evals)
            self.eval = childs_evals[ind]
            self.best_ind = ind
            return

        def get_best_move(self):
            return self.poss_moves[self.best_ind]

    def __init__(self, max_depth):
        super().__init__()
        self.max_depth = max_depth

    def _find_move(self, state: chess.State):
        root = MinMaxBot.Node(state)
        root.build_tree(self.max_depth)
        self.move = root.get_best_move()
        self.move_ready = True
        return

    def request_move(self, state: chess.State):
        thr = threading.Thread(target=self._find_move, args=(state,))
        thr.start()
        return
