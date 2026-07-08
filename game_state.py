import json
import os

SAVE_FILE = "save_file.json"
GAME_DATA_FILE = "game_data.json"

def load_save():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                if state and isinstance(state, dict):
                    # Ensure essential fields exist
                    state.setdefault('equipped_shield', 'None')
                    state.setdefault('spells', [])
                    state.setdefault('companions', [])
                    state.setdefault('history', [])
                    state.setdefault('language', 'Korean')
                    # Phase 1 Defaults
                    state.setdefault('conditions', [])
                    state.setdefault('reaction_used', False)
                    # Phase 2 Defaults
                    state.setdefault('hit_die', 8)
                    state.setdefault('hit_dice_remaining', state.get('level', 1))
                    state.setdefault('skill_proficiencies', [])
                    state.setdefault('expertise', [])
                    state.setdefault('save_proficiencies', [])
                    state.setdefault('racial_traits', ['Versatile'] if state.get('race') == 'Human' else [])
                    state.setdefault('speed', 30)
                    state.setdefault('languages', ['Common'])
                    state.setdefault('passive_perception', 10)
                    state.setdefault('class_features', {})
                    # Phase 3 Defaults
                    import skills_data
                    char_class = state.get('class', 'Fighter')
                    lvl = state.get('level', 1)
                    max_slots = skills_data.get_slots_for_class_and_level(char_class, lvl)
                    state.setdefault('spell_slots_max', max_slots)
                    state.setdefault('spell_slots', dict(max_slots))
                    state.setdefault('use_spell_slots', True)
                    state.setdefault('concentrating_on', None)
                return state
        except Exception:
            return None
    return None

def load_game_data():
    if os.path.exists(GAME_DATA_FILE):
        try:
            with open(GAME_DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"items": {}, "monsters": {}, "spells": {}}

def save_game_data(game_data):
    temp_file = GAME_DATA_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(game_data, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, GAME_DATA_FILE)
    except Exception as e:
        print(f"Error saving game data: {e}")

def save_game(state):
    temp_file = SAVE_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        os.replace(temp_file, SAVE_FILE)
    except Exception as e:
        print(f"Error saving game state: {e}")