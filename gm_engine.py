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
    6. "awarded_xp": An integer between 0 and 50. Award 0 for basic observation, moving, or starting out. ONLY award >0 XP for overcoming obstacles, finding secrets, or significant achievements.
    7. "situation_type": A string categorizing the current state. Must be exactly one of: "exploration", "combat_start", "social", or "skill_check".
    8. "spawned_monsters": If situation_type is "combat_start", provide a list of monster names (from game_data) that are attacking. Otherwise, return an empty list.
    9. "can_shop": A boolean indicating if the player is in a location where they can buy or sell items (like a town, city, or merchant stall).
    10. "required_roll": If situation_type is "skill_check", provide the 3-letter stat abbreviation required (STR, DEX, CON, INT, WIS, CHA). Otherwise, return null.
    11. "difficulty_class": If situation_type is "skill_check", provide an integer representing the DC (e.g., 10 for easy, 15 for medium, 20 for hard). Otherwise, return null.
    12. "is_safe": A boolean indicating if the current location is safe enough to take a Long Rest (e.g., an inn, town, or fortified camp).
    13. "new_monsters_data": If you spawn a monster that is NOT in the provided game_data, provide a dictionary mapping the new monster's name to its stats (requires keys: "ac" (int), "hp" (int), "xp" (int), "attack" (string, e.g. "+3 to hit, 1d6+1 damage")). If the monster is already in game_data, return null.
    14. "updated_companions": A list of strings of the names of NPCs currently traveling and fighting alongside the player. Return an empty list if alone.
    15. "updated_spells": A list of strings of the player's currently known spells or special skills. Add to this list if they learn a new ability narratively. Return the existing list otherwise.
    16. "new_spells_data": If the player learns a skill/spell NOT in game_data, provide a dictionary mapping its name to its stats (requires keys: "mp" (int, cost to use), "description" (string, e.g. "2d6 fire damage" or "Heals 1d8 HP")). Otherwise, return null.
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