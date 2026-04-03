# TRPG GeMini: Auto-DM CLI Engine

A command-line text-based Role-Playing Game powered by Google's Gemini AI. In this hybrid engine, the AI acts as a dynamic Game Master (generating narratives, choices, and world-building), while a local Python engine strictly enforces D&D-lite mechanics like combat, skill checks, leveling, and inventory management.

## ✨ Features

- **🤖 AI Game Master**: Powered by `gemini-2.5-flash`, the GM dynamically builds the story, determines when you are in a safe zone, categorizes situations, and reacts to your custom actions.
- **⚔️ D&D-Lite Mechanics**: Local d20-based combat system featuring standard attributes (STR, DEX, CON, INT, WIS, CHA), Armor Class (AC), weapon modifiers, and proficiency bonuses.
- **🎲 Dynamic Skill Checks**: The AI recognizes when you attempt something risky, sets a Difficulty Class (DC), and hands the roll over to the local engine for resolution.
- **🐉 Evolving Bestiary**: If the AI decides you encounter a monster that doesn't exist in your local files, it will generate the stats on the fly and permanently save it to your `game_data.json`.
- **🦸 Character Progression**: Full character creation (Race, Class, Background) with multiple stat-rolling methods. Earn XP, level up, increase your max HP, and boost your attributes.
- **🛍️ Inventory & Economy**: Loot gold, shop at local merchants, manage your inventory, and equip weapons and armor.
- **🏕️ Rest & Recovery**: Take Short Rests anywhere to heal partially, or Long Rests in AI-designated "safe" zones to fully recover.
- **🤝 Companions**: Travel and fight alongside NPCs who will assist you in combat.

## 📋 Prerequisites

You will need Python 3 installed on your machine, along with a few dependencies to interact with the Gemini API and load environment variables.

```bash
pip install google-genai python-dotenv
```

You must also obtain a **Gemini API Key** from Google AI Studio.

## 🚀 Setup & Installation

1. Clone or download this repository to your local machine.
2. Create a file named `.env` in the root directory of the project.
3. Add your Gemini API key to the `.env` file like this:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```
4. Run the main engine script:
   ```bash
   python trpg_engine.py
   ```

## 🎮 How to Play

When you start the game for the first time, you will be prompted to create your character. Once in the game, the AI GM will describe your surroundings and offer you 3 logical choices.

You can interact with the world by typing:
- `1`, `2`, or `3` to select one of the GM's provided options.
- **A custom action** (e.g., "I want to inspect the bookshelf for hidden levers" or "I try to persuade the guard to let us pass").

### Built-in Commands
At any prompt asking "What do you do?", you can type the following system commands:
- `status` (or `inventory`, `stats`): View your character sheet, HP, equipped items, and stats.
- `equip`: Equip a weapon or armor from your inventory.
- `use`: Consume an item (like a Health Potion) from your inventory.
- `rest`: Take a Short or Long rest to recover HP.
- `shop`: If the GM has marked your location as having merchants, this opens the local shop interface.
- `quit`: Save your progress and exit the game.

### Combat Actions
When combat initiates, the prompt will change. You can:
- `[A]ttack`: Roll a d20 to hit the enemy using your equipped weapon's stat modifier.
- `[U]se Item`: Consume a potion or use a combat item.
- `[F]lee`: Attempt to run away (50% chance of success).
- **Custom Action**: Type anything else (e.g., "I kick dirt in the goblin's eyes") to pass the action back to the AI GM to determine the outcome.

## 📂 Project Structure

- `trpg_engine.py`: The main entry point and game loop. Orchestrates the flow between the AI and local systems.
- `gm_engine.py`: Handles the prompt formatting and API communication with Google Gemini, ensuring a strict JSON response.
- `character.py`: Manages new character creation, stat generation, and the leveling-up logic.
- `combat.py`: Contains the combat loop, handling d20 attack rolls, damage calculations, and enemy AI behavior.
- `actions.py`: Handles out-of-combat system actions (status, shop, use, equip, rest).
- `skills.py`: Resolves stat-based skill checks assigned by the AI.
- `game_state.py`: Utility functions for saving and loading the player's state (`save_file.json`) and the world data (`game_data.json`).

## 💾 Save Data

The game automatically saves your progress to two local JSON files:
- `save_file.json`: Your character's current state, HP, inventory, and location.
- `game_data.json`: The world's known items and the ever-growing bestiary of monsters the AI has spawned.

To start a brand new game, simply delete or rename `save_file.json`.