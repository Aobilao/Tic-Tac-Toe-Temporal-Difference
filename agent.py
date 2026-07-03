from game import EMPTY, Game, Player, Board
import random

DEFAULT_VALUE = 0.5
WIN_REWARD = 1.0
LOSS_REWARD = 0.0
DRAW_REWARD = 0.5

# 8 phép biến đổi đối xứng của bàn cờ 3x3
SYM_INDICES = [
    (0, 1, 2, 3, 4, 5, 6, 7, 8),  # Gốc
    (6, 3, 0, 7, 4, 1, 8, 5, 2),  # Xoay 90 theo chiều kim đồng hồ
    (8, 7, 6, 5, 4, 3, 2, 1, 0),  # Xoay 180 theo chiều kim đồng hồ
    (2, 5, 8, 1, 4, 7, 0, 3, 6),  # Xoay 270 theo chiều kim đồng hồ
    (2, 1, 0, 5, 4, 3, 8, 7, 6),  # Lật dọc
    (6, 7, 8, 3, 4, 5, 0, 1, 2),  # Lật ngang
    (0, 3, 6, 1, 4, 7, 2, 5, 8),  # Chéo chính
    (8, 5, 2, 7, 4, 1, 6, 3, 0),  # Chéo phụ
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
        self,
        player: Player,
        alpha: float = 0.1,
        epsilon: float = 0.0,
        values: dict[Board, float] | None = None,
    ) -> None:
        self.player = player
        self.alpha = alpha
        self.epsilon = epsilon
        self.values: dict[Board, float] = {} if values is None else values

    def get_value(self, board: Board) -> float:
        canonical_board = get_canonical(board)
        if canonical_board in self.values:
            return self.values[canonical_board]
        return DEFAULT_VALUE

    def evaluate_moves(self, game: Game) -> list[dict]:
        evaluations = []
        for move in game.valid_moves:
            afterstate = game.board_after_move(self.player, move)
            visited = get_canonical(afterstate) in self.values
            evaluations.append(
                {
                    "move": move,
                    "afterstate": list(afterstate),
                    "value": self.get_value(afterstate),
                    "visited": visited,
                }
            )
        return evaluations

    def choose_move(self, game: Game) -> int:
        if random.random() <= self.epsilon:
            return random.choice(game.valid_moves)

        evaluations = self.evaluate_moves(game)
        best_val = max(e["value"] for e in evaluations)
        best_moves = [e["move"] for e in evaluations if e["value"] == best_val]
        return random.choice(best_moves)

    def update(self, board: Board, target_reward: float) -> None:
        canonical_board = get_canonical(board)
        old = self.get_value(canonical_board)
        self.values[canonical_board] = old + self.alpha * (target_reward - old)

    def train_from_game(self, boards: list[Board], target_reward: float) -> None:
        target = target_reward
        for board in reversed(boards):
            self.update(board, target)
            target = self.get_value(board)
