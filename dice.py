import re
import random

def get_modifier(stat_score):
    """Calculates the standard D&D ability modifier (e.g., 14 -> 2)."""
    return (stat_score - 10) // 2

def roll_from_string(description, default_val=1):
    """Parses strings like '2d4+2' or '1d4-1' and returns the total rolled."""
    if not description: return default_val
    match = re.search(r'(\d+)d(\d+)\s*([+-]\s*\d+)?', description.lower())
    if match:
        num_dice = int(match.group(1))
        sides = int(match.group(2))
        total = sum(random.randint(1, sides) for _ in range(num_dice))
        
        modifier = 0
        if match.group(3):
            mod_str = match.group(3).replace(" ", "")
            modifier = int(mod_str)
            
        return total + modifier
    return default_val

def roll_initiative(dex_score):
    """Rolls initiative: d20 + DEX modifier."""
    return random.randint(1, 20) + get_modifier(dex_score)

def roll_d20(advantage=False, disadvantage=False):
    """
    Rolls a d20, taking advantage or disadvantage into account.
    If both are True, they cancel out to a normal roll.
    Returns: (result, roll_details_string)
    """
    if advantage and disadvantage:
        advantage = disadvantage = False
    
    roll1 = random.randint(1, 20)
    
    if advantage:
        roll2 = random.randint(1, 20)
        result = max(roll1, roll2)
        detail = f"2d20({roll1},{roll2})->{result} [ADV]"
    elif disadvantage:
        roll2 = random.randint(1, 20)
        result = min(roll1, roll2)
        detail = f"2d20({roll1},{roll2})->{result} [DIS]"
    else:
        result = roll1
        detail = f"d20({result})"
        
    return result, detail

def make_saving_throw(entity_state, stat, dc, advantage=False, disadvantage=False):
    """
    Makes a D&D 5e saving throw for an entity.
    Returns: (success: bool, total: int, detail: str)
    """
    import conditions
    
    if conditions.has_effect(entity_state, 'auto_fail_str_dex_saves') and stat in ['STR', 'DEX']:
        return False, 0, f"Auto-failed {stat} save due to condition"
        
    if entity_state.get('armor_penalty') and stat in ['STR', 'DEX']:
        disadvantage = True
        
    stat_mod = get_modifier(entity_state['stats'][stat])
    
    # Check if proficient
    is_prof = stat in entity_state.get('save_proficiencies', [])
    prof_bonus = (2 + ((entity_state.get('level', 1) - 1) // 4)) if is_prof else 0
    
    roll, roll_detail = roll_d20(advantage=advantage, disadvantage=disadvantage)
    
    total = roll + stat_mod + prof_bonus
    success = total >= dc
    
    detail_str = f"{roll_detail} + {stat_mod} ({stat} mod)"
    if prof_bonus > 0:
        detail_str += f" + {prof_bonus} (Prof)"
    detail_str += f" = {total} vs DC {dc}"
    
    return success, total, detail_str