import json
import os
import google.generativeai as genai

# 1. Setup API Key 
# Replace "YOUR_API_KEY_HERE" with your actual Gemini API key.
API_KEY = "YOUR_API_KEY_HERE"
genai.configure(api_key=API_KEY)

SAVE_FILE = "save_file.json"

# 2. Initialize or Load Save Data
def load_save():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    else:
        # Default new game state is created if no save exists
        default_state = {
            "name": "Peter",
            "hp": 20,
            "level": 1,
            "inventory": ["Iron Sword", "Leather Armor", "3x Health Potion"],
            "location": "The Crossroads",
            "history": [] # Stores the last few interactions for context
        }
        save_game(default_state)
        return default_state

def save_game(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=4)

# 3. Call the Gemini API
def generate_gm_response(state, player_action):
    # Using the standard gemini model
    model = genai.GenerativeModel('gemini-2.5-flash') 

    # We build the prompt by injecting your JSON save data
    prompt = f"""
    You are the Game Master in a text-based RPG. 
    Here is the player's current character sheet and state:
    {json.dumps(state, indent=2)}
    
    The player takes the following action: "{player_action}"
    
    Respond with the narrative outcome of this action, describe the new situation, 
    and provide 3 possible choices for the player's next move. Keep the formatting clean.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 4. Main Game Loop
def main():
    print("=== CLI TRPG ENGINE INITIALIZED ===")
    state = load_save()
    print(f"Welcome back, {state['name']}! (HP: {state['hp']})")
    print("Type 'quit' at any time to save and exit.\n")
    
    # Give the GM an initial prompt to start the game
    initial_action = "Look around and assess the situation."
    
    while True:
        print("\n[The GM is generating the scenario...]\n")
        gm_response = generate_gm_response(state, initial_action)
        print(gm_response)
        
        print("\n" + "="*50)
        action = input("\nWhat do you do? (Choose an option or type your own action): ")
        
        if action.lower() == 'quit':
            print("Saving and exiting...")
            break
        
        # Update our action for the next loop
        initial_action = action
        
        # Save a brief history so the AI remembers the flow
        state["history"].append(action)
        if len(state["history"]) > 5:
            state["history"].pop(0) # Keep history short to avoid massive data packets
            
        save_game(state)

if __name__ == "__main__":
    main()