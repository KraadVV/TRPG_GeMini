import json
import os

SAVE_FILE = "save_file.json"
GAME_DATA_FILE = "game_data.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)

    return None

def load_game_data():
    if os.path.exists(GAME_DATA_FILE):
        with open(GAME_DATA_FILE, "r") as f:
            return json.load(f)
    return {"items": {}, "monsters": {}, "spells": {}}

def save_game_data(game_data):
    with open(GAME_DATA_FILE, "w") as f:
        json.dump(game_data, f, indent=4)

def save_game(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=4)