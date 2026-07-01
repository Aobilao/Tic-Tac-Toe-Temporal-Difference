Player = int
Board = tuple[int, ...]

EMPTY = 0
X = 1
O = 2

WIN_STATES = {
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
}


class Game:
    def __init__(self) -> None:
        self.board = tuple([EMPTY] * 9)
        self.valid_moves = [i for i in range(9)]

    def board_after_move(self, player: Player, pos: int) -> Board:
        board = list(self.board)
        board[pos] = player
        return tuple(board)

    def is_end(self) -> bool:
        return len(self.valid_moves) == 0 or self.winner() != EMPTY

    def update_board(self, board: Board) -> None:
        self.board = board
        self.valid_moves = [i for i in range(9) if self.board[i] == EMPTY]

    def update(self, player: Player, pos: int) -> None:
        board = self.board_after_move(player, pos)
        self.update_board(board)

    def winner(self) -> Player:
        for a, b, c in WIN_STATES:
            if (
                self.board[a] == self.board[b] == self.board[c]
                and self.board[a] != EMPTY
            ):
                return self.board[a]
        return EMPTY

    def draw_board(self) -> None:
        print("Board:")
        for i in range(3):
            for j in range(3):
                char = self.board[3 * i + j]
                if char == EMPTY:
                    char = " "
                elif char == X:
                    char = "X"
                elif char == O:
                    char = "O"
                print(char, end=" ")
            print()

    def play(self) -> None:
        player = X
        while not self.is_end():
            name = "X" if player == X else "O"
            self.draw_board()

            pos = int(input(f"Choose move as {name}: "))
            if pos not in self.valid_moves:
                print("Invalid move")
                continue

            new_board = self.board_after_move(player, pos)
            self.update_board(new_board)
            player = O if player == X else X

        if self.winner() == EMPTY:
            print("Draw")
        else:
            name = "X" if self.winner() == X else "O"
            print(f"{name} wins")
        self.draw_board()


if __name__ == "__main__":
    game = Game()
    game.play()
