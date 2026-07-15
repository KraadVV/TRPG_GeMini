import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

def generate_gm_response(state, player_action, game_data=None):
    language = state.get('language', 'Korean')
    
    prompt = f"""
    You are the Game Master in a strict D&D-lite rules-based TRPG. 
    Your role is to build the narrative, set scene contexts, and manage story progression.
    The rule-based calculations (combat rolls, skill check rolls, level ups) are calculated deterministically by the local Python engine.
    
    [IMPORTANT: LANGUAGE SETTING]
    The player's preferred language is **{language}**.
    You MUST generate the "narrative" and "choices" fields in **{language}**!
    All other JSON keys and data structures MUST remain in English as requested.
    
    Here is the player's current character sheet and state:
    {json.dumps(state, indent=2)}
    
    Here is the reference database of monsters, items, and spells:
    {json.dumps(game_data, indent=2) if game_data else "{}"}
    
    The player takes the following action: "{player_action}"
    
    Analyze this action and return a JSON object with exactly the following keys:
    1. "narrative": A string describing the outcome of the action and the new situation (written in {language}).
    2. "choices": A list of 3 strings representing the player's next logical options (written in {language}).
    3. "updated_location": A string of the current location name.
    4. "situation_type": A string categorizing the current state. Must be exactly one of: "exploration", "combat_start", "social", or "skill_check".
    5. "can_shop": A boolean indicating if the player is in a location with merchants or shops.
    6. "is_safe": A boolean indicating if the current location is safe enough for a Long Rest.
    7. "awarded_xp": An integer (0 to 50). Award XP ONLY for major narrative achievements, puzzle solving, or overcoming obstacles.
    8. "updated_inventory": A list of strings representing the player's new inventory. Add/remove items based on the narrative.
    9. "updated_companions": A list of strings of NPCs currently traveling with the player.
    10. "updated_spells": A list of spells the player currently knows.
    
    [D&D MECHANICAL EVENTS - THE PYTHON ENGINE WILL ROLL THE DICE]
    11. "damage_taken_dice": If the player takes damage from a trap, fall, poison, or environment, specify the dice notation (e.g., "1d6", "2d4+2"). If no damage was taken, return null.
    12. "heal_received_dice": If the player is healed by a mystical fountain, blessing, or potion (not manually used by player), specify the dice notation (e.g., "1d8", "2d6+2"). Otherwise, return null.
    13. "mp_used": An integer specifying if the narrative action consumed MP (e.g., casting an out-of-combat utility spell). Otherwise, return 0.
    14. "mp_recovered": An integer specifying if the player recovered MP through meditation or magical means. Otherwise, return 0.
    
    [COMBAT & SKILL INTERCEPTS]
    15. "spawned_monsters": If situation_type is "combat_start", provide a list of monster names from game_data that are attacking. Otherwise, return an empty list.
    16. "new_monsters_data": If you spawn a monster NOT in game_data, provide its name and stats as a dictionary, mapping the monster name to its stats: {{"Monster Name": {{"ac": int, "hp": int, "xp": int, "attack": string (e.g., "+3 to hit, 1d6+1 damage"), "dex": int}}}}. Otherwise, return null.
    17. "required_roll": If situation_type is "skill_check", provide the 3-letter D&D stat required (STR, DEX, CON, INT, WIS, CHA). Otherwise, return null.
    18. "required_skill": If situation_type is "skill_check" and it involves a specific skill, provide its name (Athletics, Acrobatics, Sleight of Hand, Stealth, Arcana, History, Investigation, Nature, Religion, Animal Handling, Insight, Medicine, Perception, Survival, Deception, Intimidation, Performance, Persuasion). Otherwise, return null.
    19. "difficulty_class": If situation_type is "skill_check", provide the DC (Difficulty Class) integer (e.g., 10 for easy, 15 for medium, 20 for hard). Otherwise, return null.
    
    [SPELL/SKILL LEARNING]
    20. "new_spells_data": If the player learns a new skill/spell NOT in game_data, provide its name and details as a dictionary, mapping the spell/skill name to its details: {{"Spell Name": {{"mp": int (cost), "description": string (e.g., "Heals 1d8 HP"), "level": int (0 for cantrips), "is_cantrip": bool, "save_type": string/null, "concentration": bool}}}}. Otherwise, return null.
    
    [PHASE 1 - ADVANTAGE, CONDITIONS, SURPRISE]
    21. "advantage": If situation_type is "skill_check", set to true if the situation grants Advantage. Otherwise, false.
    22. "disadvantage": If situation_type is "skill_check", set to true if the situation grants Disadvantage. Otherwise, false.
    23. "player_conditions_add": A list of dictionaries representing conditions to add to the player: [{{"name": string (e.g., "poisoned"), "duration": int/null (rounds), "source": string/null}}]. Supported conditions: blinded, charmed, deafened, frightened, grappled, incapacitated, invisible, paralyzed, petrified, poisoned, prone, restrained, stunned, unconscious.
    24. "player_conditions_remove": A list of condition names (strings) to remove from the player.
    25. "is_surprise_round": A boolean indicating if combat_start should trigger a surprise round.
    26. "surprised_side": A string indicating who is surprised, either "enemies" or "players" or null.
    """
    
    import time
    from google.genai.errors import APIError
    
    max_retries = 3
    delay = 2
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            
            if not response.text:
                raise ValueError("Empty response text from Gemini API")
                
            data = json.loads(response.text)
            if not isinstance(data, dict):
                raise ValueError("Response is not a JSON object")
                
            # Standardize / default ensure keys to prevent KeyError in main game loop
            lang = state.get('language', 'Korean')
            data.setdefault('narrative', '주변이 고요합니다.' if lang == 'Korean' else 'The world remains quiet.')
            if lang == 'Korean':
                data.setdefault('choices', ['주변을 둘러본다.', '인벤토리를 확인한다.', '휴식을 취한다.'])
            else:
                data.setdefault('choices', ['Look around.', 'Check inventory.', 'Rest.'])
            data.setdefault('updated_location', state.get('location', 'The Town'))
            data.setdefault('situation_type', 'exploration')
            data.setdefault('updated_inventory', state.get('inventory', []))
            data.setdefault('updated_companions', state.get('companions', []))
            data.setdefault('updated_spells', state.get('spells', []))
            data.setdefault('advantage', False)
            data.setdefault('disadvantage', False)
            data.setdefault('player_conditions_add', [])
            data.setdefault('player_conditions_remove', [])
            data.setdefault('is_surprise_round', False)
            data.setdefault('surprised_side', None)
            data.setdefault('required_skill', None)
            data.setdefault('required_roll', None)
            
            return data
            
        except (APIError, Exception) as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise RuntimeError(f"GM Engine failed after {max_retries} attempts: {e}")