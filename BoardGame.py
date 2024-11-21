#Example Flask App for a hexaganal tile game
#Logic is in this python file




from flask import Flask, render_template, request, redirect, jsonify
import json
import random
import os

app = Flask(__name__)

# Constants
BOARD_SIZE = 25
BOARD_ROWS = 5
BOARD_COLS = 5
SNAKES = {16: 6, 23: 10}
LADDERS = {3: 15, 8: 24}
GAME_STATE_FILE = "game_state.json"
EVENTS_LOG_FILE = "events_log.json"

# Game state (in-memory for now)
game_state = {
    "players": [],
    "current_turn": 0,
}

# Load game state from a file
def load_game_state():
    try:
        if os.path.exists(GAME_STATE_FILE):
            with open(GAME_STATE_FILE, "r") as file:
                return json.load(file)
    except FileNotFoundError:
        pass
    return game_state

# Save game state to a file
def save_game_state():
    with open(GAME_STATE_FILE, "w") as file:
        json.dump(game_state, file)

# Log events to a file
def log_event(event):
    events = []
    if os.path.exists(EVENTS_LOG_FILE):
        with open(EVENTS_LOG_FILE, "r") as file:
            try:
                events = json.load(file)
            except json.JSONDecodeError:
                pass
    events.append(event)
    with open(EVENTS_LOG_FILE, "w") as file:
        json.dump(events, file)

# Check for snakes or ladders
def check_snake_or_ladder(position):
    if position in SNAKES:
        return SNAKES[position]
    elif position in LADDERS:
        return LADDERS[position]
    return position

# Roll the dice
@app.route("/roll_dice", methods=["POST"])
def roll_dice():
    global game_state
    dice_roll = random.randint(1, 6)
    current_player = game_state["players"][game_state["current_turn"]]
    old_position = current_player["position"]
    new_position = old_position + dice_roll

    # Check for board limits
    if new_position > BOARD_SIZE:
        new_position = old_position  # Stay in the same position if they overshoot

    # Check for snakes or ladders
    new_position = check_snake_or_ladder(new_position)
    current_player["position"] = new_position

    # Log the event
    log_event({
        "player": current_player["name"],
        "dice_roll": dice_roll,
        "old_position": old_position,
        "new_position": new_position
    })

    # Check if the player won
    if new_position == BOARD_SIZE:
        save_game_state()
        return jsonify({"message": f"{current_player['name']} wins!", "dice_roll": dice_roll})

    # Update turn
    game_state["current_turn"] = (game_state["current_turn"] + 1) % len(game_state["players"])
    save_game_state()
    return jsonify({"dice_roll": dice_roll, "position": new_position})

# Start a new game
@app.route("/new_game", methods=["GET", "POST"])
def new_game():
    global game_state
    if request.method == "POST":
        num_players = int(request.form["num_players"])
        game_state["players"] = [{"name": f"Player {i+1}", "position": 0} for i in range(num_players)]
        game_state["current_turn"] = 0
        save_game_state()
        # Clear event log for a new game
        if os.path.exists(EVENTS_LOG_FILE):
            os.remove(EVENTS_LOG_FILE)
        return redirect("/game")
    return render_template("new_game.html")

# Main game page
@app.route("/game")
def game():
    global game_state
    return render_template("game.html", game_state=game_state, board_size=BOARD_SIZE)

# Automatically open the browser
import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=True)
