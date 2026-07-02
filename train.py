from game import Player, Board, Game, X, O, EMPTY
from agent import Agent, reward
import pickle
import random
import os

GAMES_AGAINST_RANDOM = 1000
TRAINING_ROUNDS = 100000


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


def train(
    agent_x: Agent,
    agent_o: Agent,
    rounds: int,
    epsilon_start: float = 0.3,
    epsilon_end: float = 0.0,
) -> None:
    for round in range(rounds):
        epsilon = epsilon_start + (epsilon_end - epsilon_start) * (round / rounds)
        agent_x.epsilon = epsilon
        agent_o.epsilon = epsilon

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
    with open(os.path.join(dir, path), "rb") as f:
        return pickle.load(f)


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

    train(agent_x, agent_o, TRAINING_ROUNDS)

    win_x, draw_x, lose_x = play_against_random(agent_x, X, GAMES_AGAINST_RANDOM)
    win_o, draw_o, lose_o = play_against_random(agent_o, O, GAMES_AGAINST_RANDOM)

    print("Against random")
    print(
        f"X: Win probability: {win_x / GAMES_AGAINST_RANDOM}, loss probability: {lose_x / GAMES_AGAINST_RANDOM}"
    )
    print(
        f"O: Win probability: {win_o / GAMES_AGAINST_RANDOM}, loss probability: {lose_o / GAMES_AGAINST_RANDOM}"
    )
    print(f"Total canonical positions explored for X: {len(agent_x.values)}")
    print(f"Total canonical positions explored for O: {len(agent_o.values)}")
    save(agent_x, agent_o)
