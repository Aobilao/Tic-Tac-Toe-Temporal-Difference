from game import EMPTY, Game, Player, Board
import random

DEFAULT_VALUE = 0.5
WIN_REWARD = 1.0
LOSS_REWARD = 0.0
DRAW_REWARD = 0.5

# 8 phép biến đổi đối xứng của bàn cờ 3x3
SYM_INDICES = [
    (0, 1, 2, 3, 4, 5, 6, 7, 8),  # Gốc
    (6, 3, 0, 7, 4, 1, 8, 5, 2),  # Xoay 90
    (8, 7, 6, 5, 4, 3, 2, 1, 0),  # Xoay 180
    (2, 5, 8, 1, 4, 7, 0, 3, 6),  # Xoay 270
    (2, 1, 0, 5, 4, 3, 8, 7, 6),  # Lật dọc
    (6, 7, 8, 3, 4, 5, 0, 1, 2),  # Lật ngang
    (0, 3, 6, 1, 4, 7, 2, 5, 8),  # Chéo chính
    (8, 5, 2, 7, 4, 1, 6, 3, 0)   # Chéo phụ
]

def get_canonical(board: Board) -> Board:
    syms = [tuple(board[i] for i in idx) for idx in SYM_INDICES]
    return min(syms)

def reward(winner: Player, player: Player):
    if winner == player:
        return WIN_REWARD
    elif winner == EMPTY:
        return DRAW_REWARD
    else:
        return LOSS_REWARD

class Agent:
    def __init__(
        self, player: Player, learning_rate: float = 0.1, exploration_prob: float = 0.1
    ) -> None:
        self.player = player
        self.alpha = learning_rate
        self.epsilon = exploration_prob
        self.values: dict[Board, float] = {}

    def get_value(self, board: Board) -> float:
        canonical_board = get_canonical(board)
        
        if canonical_board not in self.values:
            if canonical_board[4] == self.player:
                return 0.6 
            return DEFAULT_VALUE
            
        return self.values[canonical_board]

    def choose_move(self, game: Game) -> int:
        if random.random() <= self.epsilon:
            return random.choice(game.valid_moves)
        else:
            best_val = float("-inf")
            best_moves = []
            for move in game.valid_moves:
                new_board = game.board_after_move(self.player, move)
                val = self.get_value(new_board)
                if val > best_val:
                    best_val = val
                    best_moves = [move]
                elif val == best_val:
                    best_moves.append(move)
            return random.choice(best_moves)

    def update(self, board: Board, reward: float) -> None:
        canonical_board = get_canonical(board)
        old = self.get_value(canonical_board)
        self.values[canonical_board] = old + self.alpha * (reward - old)

    def train_from_game(self, boards: list[Board], reward: float) -> None:
        target = reward
        for board in reversed(boards):
            self.update(board, target)
            target = self.get_value(board)