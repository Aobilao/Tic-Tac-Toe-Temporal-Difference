import os
import pickle

from flask import Flask, request, jsonify, render_template

from game import X, O, Game
from agent import Agent

app = Flask(__name__)

here = os.path.dirname(__file__)
tables = pickle.load(open(os.path.join(here, "values.pkl"), "rb"))

bot_x = Agent(X, tables["X"])
bot_o = Agent(O, tables["O"])
bots = {X: bot_x, O: bot_o}


def status_of(game: Game, human: int, bot: int) -> str:
    won = game.winner()
    if won == human:
        return "human"
    if won == bot:
        return "bot"
    if game.is_end():
        return "draw"
    return "ongoing"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    bot_player = data["bot_player"]
    human_player = X if bot_player == O else O

    game = Game()
    game.update_board(tuple(data["board"]))

    bot_move = None
    if not game.is_end():
        bot_move = bots[bot_player].choose_move(game)
        game.update(bot_player, bot_move)

    return jsonify(
        {
            "board": list(game.board),
            "bot_move": bot_move,
            "status": status_of(game, human_player, bot_player),
        }
    )


@app.route("/review", methods=["POST"])
def review():
    data = request.get_json()
    bot_player = data["bot_player"]
    human_player = X if bot_player == O else O
    moves = data["moves"]

    game = Game()
    bot = bots[bot_player]
    decisions = []

    for ply, m in enumerate(moves, start=1):
        if game.is_end():
            break
        player, pos = m["player"], m["pos"]

        if player == bot_player:
            candidates = bot.evaluate_moves(game)
            for c in candidates:
                c["chosen"] = c["move"] == pos
            candidates.sort(key=lambda c: c["value"], reverse=True)
            decisions.append(
                {
                    "ply": ply,
                    "board_before": list(game.board),
                    "chosen_move": pos,
                    "candidates": candidates,
                }
            )

        game.update(player, pos)

    return jsonify(
        {
            "bot_player": bot_player,
            "result": status_of(game, human_player, bot_player),
            "decisions": decisions,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
