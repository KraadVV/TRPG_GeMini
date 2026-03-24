import random
import re

def handle_combat(state, game_data, gm_data):
    # Returns (survived: bool, player_action: str)
    monsters = gm_data.get('spawned_monsters')
    enemy_name = monsters[0]
    enemy_data = game_data.get("monsters", {}).get(enemy_name)
    
    if not enemy_data:
        return True, f"I prepared for battle against the {enemy_name}, but it vanished."
        
    print(f"\n⚔️  COMBAT START: {enemy_name} ⚔️")
    enemy_hp = enemy_data['hp']
    
    while enemy_hp > 0 and state['hp'] > 0:
        print(f"\n--- {enemy_name} (HP: {enemy_hp}/{enemy_data['hp']}) vs {state['name']} (HP: {state['hp']}/{state.get('max_hp', state['hp'])}) ---")
        c_action = input("Combat Action: [A]ttack, [F]lee: ").upper()
        
        if c_action == 'F':
            if random.randint(1, 20) > 10:
                print("\n[Success] You managed to run away!")
                return True, f"I successfully fled from the {enemy_name}."
            else:
                print("\n[Failed] You couldn't escape!")
                
        elif c_action == 'A':
            p_roll = random.randint(1, 20)
            str_mod = (state['stats']['STR'] - 10) // 2
            p_total = p_roll + str_mod
            print(f"\nYou rolled a {p_roll} + {str_mod} (STR mod) = {p_total} to hit vs AC {enemy_data['ac']}.")
            
            if p_total >= enemy_data['ac']:
                wpn = state.get('equipped_weapon')
                dmg_dice = 4
                if wpn and wpn in game_data.get('items', {}):
                    desc = game_data['items'][wpn]['description']
                    match = re.search(r'1d(\d+)', desc)
                    if match: dmg_dice = int(match.group(1))
                dmg = max(1, random.randint(1, dmg_dice) + str_mod)
                enemy_hp -= dmg
                print(f"Hit! You deal {dmg} damage with your {wpn if wpn and wpn != 'None' else 'fists'}.")
            else:
                print("You missed!")
        else:
            print("Invalid action. Please enter A or F.")
            continue
                
        if enemy_hp <= 0:
            print(f"\n🎉 You defeated the {enemy_name}!")
            return True, f"I fought and killed the {enemy_name}."
            
        # Monster Attack
        m_roll, m_hit_mod = random.randint(1, 20), 0
        m_atk_str = enemy_data.get('attack', '+0 to hit, 1d4 damage')
        if hit_match := re.search(r'\+(\d+)', m_atk_str): m_hit_mod = int(hit_match.group(1))
        m_total = m_roll + m_hit_mod
        print(f"\n{enemy_name} attacks! Rolls {m_roll} + {m_hit_mod} = {m_total} to hit vs your AC {state.get('ac', 10)}.")
        
        if m_total >= state.get('ac', 10):
            dmg_match = re.search(r'1d(\d+)\+?(\d*)', m_atk_str)
            m_dmg = max(1, random.randint(1, int(dmg_match.group(1))) + (int(dmg_match.group(2)) if dmg_match.group(2) else 0)) if dmg_match else max(1, random.randint(1, 4))
            state['hp'] -= m_dmg
            print(f"Ouch! {enemy_name} hits! You take {m_dmg} damage.")
        else: print(f"{enemy_name} misses!")
    return state['hp'] > 0, ""