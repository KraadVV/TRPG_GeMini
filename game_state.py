import json
import os

SAVE_FILE = "save_file.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)

    return None

def save_game(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=4)