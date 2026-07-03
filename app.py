from flask import Flask, request, jsonify, render_template

from game import X, O, Game, Player
from agent import Agent
from train import load

app = Flask(__name__)

tables = load()

bot_x = Agent(X, values=tables["X"])
bot_o = Agent(O, values=tables["O"])
bots = {X: bot_x, O: bot_o}


def status_of(game: Game, human: Player, bot: Player) -> str:
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
    decisions = []

    for ply, m in enumerate(moves, start=1):
        if game.is_end():
            break
        player, pos = m["player"], m["pos"]

        evaluator_bot = bots[player]
        candidates = evaluator_bot.evaluate_moves(game)

        best_val = -float("inf")
        chosen_val = 0

        for c in candidates:
            if c["value"] > best_val:
                best_val = c["value"]
            c["chosen"] = c["move"] == pos
            if c["chosen"]:
                chosen_val = c["value"]

        diff = best_val - chosen_val
        if diff <= 0.05:
            quality = "Excellent 🌟"
            q_class = "q-excellent"
        elif diff < 0.4:
            quality = "Inaccuracy ⚠️"
            q_class = "q-inaccuracy"
        else:
            quality = "Blunder 💀"
            q_class = "q-blunder"

        candidates.sort(key=lambda c: c["value"], reverse=True)
        decisions.append(
            {
                "ply": ply,
                "player": player,
                "is_human": player == human_player,
                "board_before": list(game.board),
                "chosen_move": pos,
                "candidates": candidates,
                "quality": quality,
                "q_class": q_class,
            }
        )

        game.update(player, pos)

    return jsonify(
        {
            "bot_player": bot_player,
            "human_player": human_player,
            "result": status_of(game, human_player, bot_player),
            "decisions": decisions,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
