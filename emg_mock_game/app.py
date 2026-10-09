from flask import Flask, jsonify, render_template, request

from emg.mock_provider import MockEMGProvider
from game.controller import GameController

app = Flask(__name__)
game = GameController()
mock_provider = MockEMGProvider()


def error(message: str, status: int = 400):
    return jsonify({"error": message}), status


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/emg")
def update_emg():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return error("A JSON object is required.")
    try:
        biceps = float(payload["biceps"])
        triceps = float(payload["triceps"])
    except (KeyError, TypeError, ValueError):
        return error("biceps and triceps must be numeric values.")
    return jsonify(game.update_emg(biceps, triceps, payload.get("input_mode")))


@app.get("/api/mock")
def mock_sample():
    biceps, triceps = mock_provider.get_sample()
    return jsonify(game.update_emg(biceps, triceps, "auto"))


@app.get("/api/state")
def state():
    return jsonify(game.snapshot())


@app.post("/api/control")
def control():
    payload = request.get_json(silent=True) or {}
    action = payload.get("action")
    if action not in {"start", "pause"}:
        return error("action must be start or pause.")
    return jsonify(game.set_game_state(action))


@app.post("/api/score")
def score():
    return jsonify(game.add_score(100))


@app.post("/api/reset")
def reset():
    return jsonify(game.reset())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

