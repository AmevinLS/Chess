import chess
import numpy as np


class RandomBot:
    def __init__(self):
        return
    
    def get_move(self, state: chess.State):
        poss_moves = state.get_possible_moves()
        ind = np.random.randint(0, len(poss_moves))
        return poss_moves[ind]


class MinMaxBot:
    class Node:
        def __init__(self, state: chess.State):
            self.state = state
            self.eval = state.get_imbalance()
            self.childs = []

        def _create_childs(self):
            self.poss_moves = self.state.get_possible_moves()
            for move in self.poss_moves:
                self.childs.append(MinMaxBot.Node(self.state.make_move(move)))

        def build_tree(self, max_depth, depth=0):
            if depth >= max_depth:
                return

            self._create_childs()
            for child in self.childs:
                child.build_tree(max_depth, depth+1)

            childs_evals = [child.eval for child in self.childs]
            if self.state.color_to_move == chess.Color.WHITE:
                ind = np.argmax(childs_evals)
            else:
                ind = np.argmin(childs_evals)
            self.eval = childs_evals[ind]
            self.best_ind = ind
            return

        def get_best_move(self):
            return self.poss_moves[self.best_ind]

    def __init__(self):
        return

    def get_move(self, state: chess.State, max_depth):
        root = MinMaxBot.Node(state)
        root.build_tree(max_depth)
        move = root.get_best_move()
        return move
