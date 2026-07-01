from game import Player, Board, Game, X, O, EMPTY
from agent import Agent, reward
import pickle
import random
import os


def play_game(
    agent_x: Agent, agent_o: Agent
) -> tuple[dict[Player, list[Board]], Player]:
    game = Game()
    agents = {X: agent_x, O: agent_o}
    state_history: dict[Player, list[Board]] = {X: [], O: []}

    player = X
    while not game.is_end():
        move = agents[player].choose_move(game)
        game.update(player, move)
        state_history[player].append(game.board)
        player = O if player == X else X

    return state_history, game.winner()


def train(agent_x: Agent, agent_o: Agent, rounds: int):
    for _ in range(rounds):
        state_history, winner = play_game(agent_x, agent_o)

        reward_x = reward(winner, X)
        reward_o = reward(winner, O)

        agent_x.train_from_game(state_history[X], reward_x)
        agent_o.train_from_game(state_history[O], reward_o)


def save(agent_x: Agent, agent_o: Agent, path: str = "values.pkl") -> None:
    with open(path, "wb") as f:
        pickle.dump({"X": agent_x.values, "O": agent_o.values}, f)


def load(path: str = "values.pkl"):
    dir = os.path.dirname(__file__)
    return pickle.load(open(os.path.join(dir, path), "rb"))


def play_against_random(
    agent: Agent, agent_player: Player, rounds: int
) -> tuple[int, int, int]:
    win = draw = lose = total = 0
    saved_epsilon = agent.epsilon
    agent.epsilon = 0

    for _ in range(rounds):
        game = Game()
        player = X
        while not game.is_end():
            if agent_player == player:
                pos = agent.choose_move(game)
                game.update(player, pos)
            else:
                pos = random.choice(game.valid_moves)
                game.update(player, pos)
            player = O if player == X else X

        winner = game.winner()
        if winner == agent_player:
            win += 1
        elif winner == EMPTY:
            draw += 1
        else:
            lose += 1

        total += 1

    agent.epsilon = saved_epsilon
    return win, draw, lose


if __name__ == "__main__":
    agent_x = Agent(X)
    agent_o = Agent(O)

    train(agent_x, agent_o, 10000)

    games_against_random = 1000
    win, draw, lose = play_against_random(agent_x, X, games_against_random)
    print("Against random:")
    print(
        f"Win probability: {win / games_against_random}, non-loss: {(draw + win) / games_against_random}"
    )
    save(agent_x, agent_o)
