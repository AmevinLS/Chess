# flake8: noqa
import numpy as np
from enum import Enum
from copy import deepcopy


class BadMoveError(Exception):
    pass


class Color(Enum):
    NONE = "none"
    WHITE = "white"
    BLACK = "black"


class Piece:
    class Kind(Enum):
        EMPTY = "empty"
        PAWN = "pawn"
        KNIGHT = "knight"
        BISHOP = "bishop"
        ROOK = "rook"
        QUEEN = "queen"
        KING = "king"

    def __init__(self, kind, color=None):
        if isinstance(kind, str):  # Parsing "kind" argument
            self.kind = Piece.Kind(kind)
        elif isinstance(kind, Piece.Kind):
            self.kind = kind
        else:
            raise TypeError(f"Unsupported type {type(kind)} for kind of piece")

        if self.kind == Piece.Kind.EMPTY:  # set color to NONE if piece is empty
            self.color = Color.NONE
            return

        if isinstance(color, str):  # Parsing "color" argument
            self.color = Color(color)
        elif isinstance(color, Color):
            self.color = color
        else:
            raise TypeError(f"Unsupported type {type(color)} for color of piece")

        if self.kind != Piece.Kind.EMPTY and self.color == Color.NONE:
            raise ValueError("Non-EMPTY piece can't be of color NONE")

    def __str__(self):
        kind = self.kind
        if kind == Piece.Kind.EMPTY:
            return "_"
        elif kind == Piece.Kind.PAWN:
            return "P"
        elif kind == Piece.Kind.KNIGHT:
            return "N"
        elif kind == Piece.Kind.BISHOP:
            return "B"
        elif kind == Piece.Kind.ROOK:
            return "R"
        elif kind == Piece.Kind.QUEEN:
            return "Q"
        elif kind == Piece.Kind.KING:
            return "K"


class State:
    class Condition(Enum):
        ONGOING = "ongoing"
        CHECKMATE = "checkmate"
        STALEMATE = "stalemate"

    def __init__(self, state="initial"):
        if state == "empty":
            # Create board of empty here
            self.board = [[Piece("empty") for _ in range(8)] for _ in range(8)]
            self.color_to_move = Color.WHITE
            self.castle_rights = {
                Color.WHITE: {"short": True, "long": True},
                Color.BLACK: {"short": True, "long": True}
            }
        elif state == "initial":
            # Create the standard starting position
            backrank_kinds = [
                "rook", "knight", "bishop", "queen",
                "king", "bishop", "knight", "rook"
            ]
            self.board = []
            self.board.append([Piece(kind, "black") for kind in backrank_kinds])
            self.board.append([Piece("pawn", "black")] * 8)
            for _ in range(4):
                self.board.append([Piece("empty")] * 8)
            self.board.append([Piece("pawn", "white")] * 8)
            self.board.append([Piece(kind, "white") for kind in backrank_kinds])
            self.color_to_move = Color.WHITE
            self.castle_rights = {
                Color.WHITE: {"short": True, "long": True},
                Color.BLACK: {"short": True, "long": True}
            }
            self.condition = State.Condition.ONGOING
            self.en_peas_sqrs = []

    def __str__(self):
        res = ""
        for line in self.board:
            for piece in line:
                res += str(piece) + " "
            res += "\n"
        return res

    def _square_to_coords(self, sqr):
        """
        Returns board coordinate converted to square coordinate
            Parameter:
                sqr (str): Board coordinate like "f6"
            Returns:
                (x, y) (tuple): Matrix coordinates of board (from top-left corner)
        """
        y = ord(sqr[0]) - ord("a")
        x = 8 - int(sqr[1])
        return (x, y)

    def _get_opposite_color(self, color):
        if color == Color.WHITE:
            return Color.BLACK
        elif color == Color.BLACK:
            return Color.WHITE
        elif color == Color.NONE:
            return Color.NONE

    def _get_path(self, move):
        """
        Return squares a piece has to go through for move
            Parameters:
                move ([x1, y1, x2, y2]): Move made in matrix coords
            Returns:
                [(x0, y0), (x1, y1)] (list of tuples): List of coordinates the piece would have to go through
        """
        x1, y1, x2, y2 = move
        x_step = np.sign(x2 - x1)
        y_step = np.sign(y2 - y1)

        path = []
        num_steps = max(abs(x2-x1), abs(y2-y1))
        temp_x, temp_y = x1, y1
        for _ in range(num_steps-1):
            temp_x += x_step
            temp_y += y_step
            path.append((temp_x, temp_y))
        return path

    def _is_valid_path(self, path):
        for x, y in path:
            piece = self.board[x][y]
            if piece.kind != Piece.Kind.EMPTY:
                return False
        return True

    def _execute_move(self, move):
        x1, y1, x2, y2 = move

        res_state = deepcopy(self)
        

        # Processing castling
        delta_x, delta_y = x2 - x1, y2 - y1
        piece = res_state.board[x1][y1]
        if piece.kind == Piece.Kind.KING:
            res_state.castle_rights[piece.color]["short"] = False
            res_state.castle_rights[piece.color]["long"] = False
            if delta_y == 2:
                res_state.board[x2][y2-1] = res_state.board[x2][y2+1]
                res_state.board[x2][y2+1] = Piece("empty")
            elif delta_y == -2:
                res_state.board[x2][y2+1] = res_state.board[x2][y2-2]
                res_state.board[x2][y2-2] = Piece("empty")
        if piece.kind == Piece.Kind.ROOK:
            if y1 == 0:
                res_state.castle_rights[piece.color]["long"] = False
            elif y1 == 7:
                res_state.castle_rights[piece.color]["short"] = False

        # Processing the general case
        res_state.board[x2][y2] = res_state.board[x1][y1]
        res_state.board[x1][y1] = Piece("empty")

        # Processing pawn stuff
        res_state.en_peas_sqrs = []
        if piece.kind == Piece.Kind.PAWN:
            if abs(delta_x) == 2:
                res_state.en_peas_sqrs.append((x2 - delta_x//2, y2))
            elif (x2, y2) in self.en_peas_sqrs:
                res_state.board[x1][y2] = Piece("empty")
            queening = False
            if piece.color == Color.WHITE and x2 == 0:
                queening = True
            elif piece.color == Color.BLACK and x2 == 7:
                queening = True 
            if queening:               
                res_state.board[x2][y2] = Piece("queen", piece.color)

        res_state.color_to_move = self._get_opposite_color(self.color_to_move)
        return res_state

    def _find_king(self, color):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                piece = self.board[i][j]
                if piece.kind == Piece.Kind.KING and piece.color == color:
                    return (i, j)
        raise Exception("Tried to find king, but no such king on board")

    def _is_valid_coords(self, x, y):
        return (x in range(0, 8)) and (y in range(0, 8))

    def _is_check_present(self, color):
        # TODO Finish this function
        king_x, king_y = self._find_king(color)
        other_color = self._get_opposite_color(color)

        # Process row/column
        for step_x, step_y in [(1, 0), (0, -1), (-1, 0), (0, 1)]:
            temp_x, temp_y = king_x+step_x, king_y+step_y
            while self._is_valid_coords(temp_x, temp_y):
                piece = self.board[temp_x][temp_y]
                if piece.kind == Piece.Kind.EMPTY:
                    temp_x += step_x
                    temp_y += step_y
                    continue
                if piece.color == color:
                    break
                if piece.kind in [Piece.Kind.BISHOP, Piece.Kind.PAWN, Piece.Kind.KNIGHT, Piece.Kind.KING]:
                    break
                if piece.kind in [Piece.Kind.ROOK, Piece.Kind.QUEEN]:
                    return True

        # Process diagonals
        for step_x, step_y in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            temp_x, temp_y = king_x+step_x, king_y+step_y
            while self._is_valid_coords(temp_x, temp_y):
                piece = self.board[temp_x][temp_y]
                if piece.kind == Piece.Kind.EMPTY:
                    temp_x += step_x
                    temp_y += step_y
                    continue
                if piece.color == color:
                    break
                if piece.kind in [Piece.Kind.ROOK, Piece.Kind.PAWN, Piece.Kind.KNIGHT]:
                    break
                if piece.kind in [Piece.Kind.BISHOP, Piece.Kind.QUEEN]:
                    return True

        # Process Knights
        for delta_x, delta_y in [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]:
            temp_x, temp_y = king_x+delta_x, king_y+delta_y
            if not self._is_valid_coords(temp_x, temp_y):
                continue
            piece = self.board[temp_x][temp_y]
            if piece.kind == Piece.Kind.KNIGHT and piece.color == other_color:
                return True

        # Process adjacent other-color king
        for delta_x, delta_y in [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]:
            temp_x, temp_y = king_x+delta_x, king_y+delta_y
            if not self._is_valid_coords(temp_x, temp_y):
                continue
            piece = self.board[temp_x][temp_y]
            if piece.kind == Piece.Kind.KING and piece.color == other_color:
                return True

        # Process pawns
        if color == Color.WHITE:
            pawn_deltas = [(-1, -1), (-1, 1)]
        elif color == Color.BLACK:
            pawn_deltas = [(1, -1), (1, 1)]
        for delta_x, delta_y in pawn_deltas:
            temp_x, temp_y = king_x+delta_x, king_y+delta_y
            if not self._is_valid_coords(temp_x, temp_y):
                continue
            piece = self.board[temp_x][temp_y]
            if piece.kind == Piece.Kind.PAWN and piece.color == other_color:
                return True

        return False

    def make_move(self, _move):
        if isinstance(_move, str):
            # Process string of type "a2-a4"
            # TODO: Add regex check for correct type of string
            crds1 = self._square_to_coords(_move[:2])
            crds2 = self._square_to_coords(_move[-2:])
            move = list(crds1) + list(crds2)
        elif isinstance(_move, tuple):
            # Process of type ("a2", "a4")
            crds1 = self._square_to_coords(_move[0])
            crds2 = self._square_to_coords(_move[1])
            move = list(crds1) + list(crds2)
        elif isinstance(_move, list):
            # Process list of type [x1, y1, x2, y2]
            move = _move
        
        if not self.is_valid_move(move):
            raise BadMoveError(f"{_move} is not a valid move")

        res_state = self._execute_move(move)

        # Changing condition of res_state
        check_present = res_state._is_check_present(res_state.color_to_move)
        poss_moves = res_state.get_possible_moves()
        if len(poss_moves) == 0:
            if check_present:
                res_state.condition = State.Condition.CHECKMATE
            else:
                res_state.condition = State.Condition.STALEMATE
        
        return res_state

    def is_valid_move(self, move):
        """Accepts move in form [x1, y1, x2, y2]"""

        x1, y1, x2, y2 = move
        piece = self.board[x1][y1]
        kind = piece.kind
        color = piece.color

        if color != self.color_to_move:  # Only the correct color can move
            return False

        if self.board[x2][y2].color == self.color_to_move:  # You can't move onto your own piece
            return False

        # First check if move is possible in general
        other_color = self._get_opposite_color(color)
        delta_x = x2 - x1
        delta_y = y2 - y1
        if delta_x == 0 and delta_y == 0:
            return False

        if kind == Piece.Kind.PAWN:
            if color == Color.WHITE:
                attack_deltas = [(-1, -1), (-1, 1)]
                push_delta = [(-1, 0)]
                first_push_delta = [(-2, 0)]
            elif color == Color.BLACK:
                attack_deltas = [(1, 1), (1, -1)]
                push_delta = [(1, 0)]
                first_push_delta = [(2, 0)]

            if (delta_x, delta_y) not in (attack_deltas + push_delta + first_push_delta):
                return False
            if ((delta_x, delta_y) in push_delta) and (self.board[x2][y2].kind != Piece.Kind.EMPTY):
                return False
            if ((delta_x, delta_y) in attack_deltas):
                if (x2, y2) in self.en_peas_sqrs:
                    pass
                elif self.board[x2][y2].color != other_color:
                    return False           
            elif (delta_x, delta_y) in first_push_delta:
                if color == Color.WHITE and x1 != 6:
                    return False
                elif color == Color.BLACK and x1 != 1:
                    return False
                if self.board[x2][y2].kind != Piece.Kind.EMPTY:
                    return False
                path = self._get_path(move)
                if not self._is_valid_path(path):
                    return False

            # TODO: finish possible pawn moves
        elif kind == Piece.Kind.KNIGHT:
            if (abs(delta_x), abs(delta_y)) not in [(1, 2), (2, 1)]:  # Knights can only move in L-shape
                return False
        elif kind == Piece.Kind.BISHOP:
            if abs(delta_x) != abs(delta_y):  # Bishops only move diagonally
                return False
            path = self._get_path(move)
            if not self._is_valid_path(path):
                return False
        elif kind == Piece.Kind.ROOK:
            if delta_x != 0 and delta_y != 0:  # Rooks only move vertically/horizontally
                return False
            path = self._get_path(move)
            if not self._is_valid_path(path):
                return False
        elif kind == Piece.Kind.QUEEN:
            if delta_x == 0 or delta_y == 0:  # Queens can move diagonally/vertically/horizontally
                pass
            elif abs(delta_x) == abs(delta_y):
                pass
            else:
                return False
            path = self._get_path(move)
            if not self._is_valid_path(path):
                return False
        elif kind == Piece.Kind.KING:
            if (abs(delta_x), abs(delta_y)) in [(0, 1), (1, 0), (1, 1)]:
                pass
            elif (delta_x, delta_y) == (0, 2):  # Process short-castling
                if not self.castle_rights[color]["short"]:
                    return False
                if self._is_check_present(color):
                    return False
                for i in [1, 2]:
                    temp_x, temp_y = x1, y1
                    temp_y += i
                    temp_piece = self.board[temp_x][temp_y]
                    if temp_piece.kind != Piece.Kind.EMPTY:
                        return False
                    temp_state = deepcopy(self)
                    temp_state.board[temp_x][temp_y] = temp_state.board[temp_x][temp_y - i]
                    temp_state.board[temp_x][temp_y - i] = Piece("empty")
                    if temp_state._is_check_present(color):
                        return False
            elif (delta_x, delta_y) == (0, -2):  # Process long-castling
                if not self.castle_rights[color]["long"]:
                    return False
                if self._is_check_present(color):
                    return False
                if self.board[x1][y1 - 3].kind != Piece.Kind.EMPTY:
                    return False                
                for i in [-1, -2]:
                    temp_x, temp_y = x1, y1
                    temp_y += i
                    temp_piece = self.board[temp_x][temp_y]
                    if temp_piece.kind != Piece.Kind.EMPTY:
                        return False
                    temp_state = deepcopy(self)
                    temp_state.board[temp_x][temp_y] = temp_state.board[temp_x][temp_y - i]
                    temp_state.board[temp_x][temp_y - i] = Piece("empty")
                    if temp_state._is_check_present(color):
                        return False
            else:
                return False
            # TODO: add possibility for castling

        # Check if the move creates/leaves a check on the player who moved
        temp_state = self._execute_move(move)
        if temp_state._is_check_present(self.color_to_move):
            return False

        return True

    def get_possible_moves(self):
        all_sqrs = []
        for i in range(8):
            for j in range(8):
                all_sqrs.append([i, j])

        poss_moves = []
        for sqr1 in all_sqrs:
            for sqr2 in all_sqrs:
                move = sqr1 + sqr2
                if self.is_valid_move(move):
                    poss_moves.append(move)
        
        return poss_moves

    def get_imbalance(self):
        color_mult = {
            Color.WHITE: 1,
            Color.BLACK: -1,
            Color.NONE: 0
        }
        piece_values = {
            Piece.Kind.QUEEN: 9, 
            Piece.Kind.ROOK: 5, 
            Piece.Kind.BISHOP: 3,
            Piece.Kind.KNIGHT: 3,
            Piece.Kind.PAWN: 1,
            Piece.Kind.KING: 0,
            Piece.Kind.EMPTY: 0
        }
        res = 0
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                res += color_mult[piece.color] * piece_values[piece.kind]
        return res


class Game:
    def __init__(self):
        self.move_counter = 0
        self.history = []
        self.states = [State("initial")]
        return

    def __str__(self):
        res = str(self.states[-1])
        res += f"Move number:\t{self.move_counter//2 + 1}\n"
        res += f"To-move:\t{self.states[-1].color_to_move}\n"
        return res

    def play_move(self, move):
        """
        Tries to make a move
            Parameters:
                move (str): a move in the form "a2-a4"
            Returns:
                (bool): whether it was possible to make the move
        """
        try:
            new_state = self.states[-1].make_move(move)
        except BadMoveError:
            print(f"Unable to make move '{move}'")
            return False
        else:
            self.states.append(new_state)
            self.move_counter += 1
            self.history.append(move)
            return True

    def play_sequence(self, seq):
        """
        Tries to make a sequence of moves:
            Parameters:
                seq (str): a sequence of moves in the form "e2-e4;e7-e5;b1-c3"
            Returns:
                (bool): whether it was possible make this sequence of moves
        """
        for m in seq.split(";"):
            if not self.make_move(m):
                return False
        return True

    def get_state(self):
        return self.states[-1]

    def get_board(self):
        return self.states[-1].board
    
    def get_history(self):
        return self.history

    def get_condition(self):
        return self.states[-1].condition