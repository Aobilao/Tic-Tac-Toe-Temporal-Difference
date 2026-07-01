import os
import pickle

from flask import Flask, request, jsonify, render_template

from game import X, O, Game
from agent import Agent

app = Flask(__name__)

here = os.path.dirname(__file__)
tables = pickle.load(open(os.path.join(here, "values.pkl"), "rb"))

bot_x = Agent(X)
bot_x.values = tables["X"]
bot_x.epsilon = 0

bot_o = Agent(O)
bot_o.values = tables["O"]
bot_o.epsilon = 0

bots = {X: bot_x, O: bot_o}


def status_of(game: Game, human: int, bot: int) -> str:
    """Describe how the game stands, for the page to display."""
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

    if not game.is_end():
        pos = bots[bot_player].choose_move(game)
        game.update(bot_player, pos)

    return jsonify(
        {
            "board": list(game.board),
            "status": status_of(game, human_player, bot_player),
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
