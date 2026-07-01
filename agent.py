from game import EMPTY, Game, Player, Board
import random

DEFAULT_VALUE = 0.5

WIN_REWARD = 1.0
LOSS_REWARD = 0.0
DRAW_REWARD = 0.5


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
        return self.values.get(board, DEFAULT_VALUE)

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
        old = self.get_value(board)
        self.values[board] = old + self.alpha * (reward - old)

    def train_from_game(self, boards: list[Board], reward: float) -> None:
        target = reward
        for board in reversed(boards):
            self.update(board, target)
            target = self.get_value(board)
