import random
import re
import actions

def handle_combat(state, game_data, gm_data):
    # Returns (survived: bool, player_action: str)
    monsters = gm_data.get('spawned_monsters')
    if not monsters:
        return True, "The enemies are nowhere to be seen."
        
    enemy_name = monsters[0]
    enemy_data = game_data.get("monsters", {}).get(enemy_name)
    
    if not enemy_data:
        return True, f"I prepared for battle against the {enemy_name}, but it vanished."
        
    # Check if we are continuing a fight against the same monster
    if state.get('active_enemy_name') == enemy_name:
        enemy_hp = state.get('active_enemy_hp', enemy_data['hp'])
    else:
        enemy_hp = enemy_data['hp']
        state['active_enemy_name'] = enemy_name

    print(f"\n⚔️  COMBAT START: {enemy_name} ⚔️")
    
    while enemy_hp > 0 and state['hp'] > 0:
        print(f"\n--- {enemy_name} (HP: {enemy_hp}/{enemy_data['hp']}) vs {state['name']} (HP: {state['hp']}/{state.get('max_hp', state['hp'])}) ---")
        c_action = input("Combat Action: [A]ttack, [U]se Item, [F]lee, or type a custom action (e.g., 'I throw sand at it'): ")
        
        if c_action.upper() == 'F':
            if random.randint(1, 20) > 10:
                print("\n[Success] You managed to run away!")
                state.pop('active_enemy_name', None)
                state.pop('active_enemy_hp', None)
                return True, f"I successfully fled from the {enemy_name}."
            else:
                print("\n[Failed] You couldn't escape!")
                
        elif c_action.upper() == 'A':
            p_roll = random.randint(1, 20)
            wpn = state.get('equipped_weapon')
            wpn_name = wpn.lower() if wpn and wpn != 'None' else ''
            c_class = state.get('class', '').lower()
            
            str_mod = (state['stats']['STR'] - 10) // 2
            dex_mod = (state['stats']['DEX'] - 10) // 2
            int_mod = (state['stats']['INT'] - 10) // 2
            wis_mod = (state['stats']['WIS'] - 10) // 2
            cha_mod = (state['stats']['CHA'] - 10) // 2
            
            spell_mod, spell_stat = int_mod, "INT"
            if any(x in c_class for x in ['cleric', 'druid', 'ranger']): spell_mod, spell_stat = wis_mod, "WIS"
            elif any(x in c_class for x in ['bard', 'paladin', 'sorcerer', 'warlock']): spell_mod, spell_stat = cha_mod, "CHA"
            
            if any(x in wpn_name for x in ['bow', 'crossbow', 'sling', 'dart']):
                combat_mod, stat_name = dex_mod, "DEX"
            elif any(x in wpn_name for x in ['dagger', 'rapier', 'shortsword', 'whip']):
                combat_mod, stat_name = (dex_mod, "DEX") if dex_mod > str_mod else (str_mod, "STR")
            elif any(x in wpn_name for x in ['staff', 'wand', 'tome']) or (not wpn_name and any(x in c_class for x in ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard'])):
                combat_mod, stat_name = spell_mod, spell_stat
            else:
                combat_mod, stat_name = str_mod, "STR"
                
            prof_bonus = 2 + ((state.get('level', 1) - 1) // 4) # D&D proficiency scaling
            p_total = p_roll + combat_mod + prof_bonus
            
            print(f"\nYou rolled a {p_roll} + {combat_mod} ({stat_name} mod) + {prof_bonus} (Prof) = {p_total} to hit vs AC {enemy_data['ac']}.")
            
            if p_total >= enemy_data['ac']:
                dmg_dice = 4
                if wpn and wpn in game_data.get('items', {}):
                    desc = game_data['items'][wpn]['description']
                    match = re.search(r'1d(\d+)', desc)
                    if match: dmg_dice = int(match.group(1))
                dmg = max(1, random.randint(1, dmg_dice) + combat_mod)
                enemy_hp -= dmg
                print(f"Hit! You deal {dmg} damage with your {wpn if wpn and wpn != 'None' else 'fists'}.")
            else:
                print("You missed!")
        elif c_action.upper() == 'U':
            if not actions.handle_use(state, game_data):
                continue
        elif len(c_action.strip()) > 1:
            print(f"\n[Handing over to the GM: '{c_action}']")
            state['active_enemy_hp'] = enemy_hp
            return True, c_action
        else:
            print("Invalid action.")
            continue
                
        # Companion Attacks
        for comp in state.get('companions', []):
            if enemy_hp <= 0: break
            if random.randint(1, 20) >= 10: # Flat 50% chance to hit
                c_dmg = random.randint(1, 6) # Base 1d6 damage
                enemy_hp -= c_dmg
                print(f"🤝 {comp} attacks and hits! Deals {c_dmg} damage to {enemy_name}.")
            else:
                print(f"💨 {comp} attacks but misses!")

        if enemy_hp <= 0:
            print(f"\n🎉 You defeated the {enemy_name}!")
            state.pop('active_enemy_name', None)
            state.pop('active_enemy_hp', None)
            return True, f"I fought and killed the {enemy_name}."
            
        # Monster Attack
        m_roll, m_hit_mod = random.randint(1, 20), 0
        m_atk_str = enemy_data.get('attack', '+0 to hit, 1d4 damage')
        if hit_match := re.search(r'\+(\d+)', m_atk_str): m_hit_mod = int(hit_match.group(1))
        m_total = m_roll + m_hit_mod
        
        # Choose Target (Player or Companions)
        targets = [state['name']] + state.get('companions', [])
        target = random.choice(targets)
        
        if target == state['name']:
            print(f"\n{enemy_name} attacks YOU! Rolls {m_roll} + {m_hit_mod} = {m_total} to hit vs your AC {state.get('ac', 10)}.")
            if m_total >= state.get('ac', 10):
                dmg_match = re.search(r'1d(\d+)\+?(\d*)', m_atk_str)
                m_dmg = max(1, random.randint(1, int(dmg_match.group(1))) + (int(dmg_match.group(2)) if dmg_match.group(2) else 0)) if dmg_match else max(1, random.randint(1, 4))
                state['hp'] -= m_dmg
                print(f"Ouch! {enemy_name} hits! You take {m_dmg} damage.")
            else: print(f"{enemy_name} misses!")
        else:
            print(f"\n{enemy_name} attacks your companion, {target}!")
            if m_total >= 13: # Flat AC 13 for companions to keep it simple
                print(f"Ouch! {enemy_name} hits {target}!")
            else:
                print(f"{enemy_name} misses {target}!")
    return state['hp'] > 0, ""