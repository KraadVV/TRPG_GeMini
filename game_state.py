import json
import os

SAVE_FILE = "save_file.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    else:
        default_state = {
            "name": "Peter",
            "hp": 20,
            "level": 1,
            "inventory": ["Iron Sword", "Leather Armor", "Health Potion"],
            "location": "The Crossroads",
            "history": [] 
        }
        save_game(default_state)
        return default_state

def save_game(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=4)