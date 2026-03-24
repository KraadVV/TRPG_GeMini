import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

def generate_gm_response(state, player_action, game_data=None):
    prompt = f"""
    You are the Game Master in a text-based RPG. 
    Here is the player's current character sheet and state:
    {json.dumps(state, indent=2)}
    
    Here is the reference data for monsters and items in the game:
    {json.dumps(game_data, indent=2) if game_data else "{}"}
    
    The player takes the following action: "{player_action}"
    
    Process the action and return a JSON object with exactly the following keys:
    1. "narrative": A string describing the outcome of the action and the new situation.
    2. "choices": A list of 3 strings representing the player's next logical options.
    3. "updated_hp": An integer of the player's new HP (subtract if they take damage, add if they heal).
    4. "updated_inventory": A list of strings of the player's new inventory (add/remove items based on the narrative).
    5. "updated_location": A string of the current location name.
    6. "awarded_xp": An integer between 0 and 50 representing experience points gained from this action (award more for overcoming challenges or clever roleplay).
    """
    
    # We pass the types config to force the API to output strict JSON
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        )
    )
    
    # Python takes the JSON string from the API and converts it into a usable dictionary
    return json.loads(response.text)