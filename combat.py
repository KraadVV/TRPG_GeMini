import random
import re
import actions
import dice

def handle_combat(state, game_data, gm_data):
    monsters = gm_data.get('spawned_monsters')
    
    if not monsters and not state.get('active_enemies'):
        return True, "The enemies are nowhere to be seen."
        
    # Initialize active enemies if starting a new fight
    if not state.get('active_enemies'):
        active_enemies = {}
        counts = {}
        for m_name in monsters:
            if m_name not in game_data.get("monsters", {}):
                continue
            counts[m_name] = counts.get(m_name, 0) + 1
            unique_name = f"{m_name} {counts[m_name]}" if monsters.count(m_name) > 1 else m_name
            active_enemies[unique_name] = {
                "type": m_name,
                "hp": game_data["monsters"][m_name]["hp"]
            }
        if not active_enemies:
            return True, "The enemies fled before you could strike."
        state['active_enemies'] = active_enemies

    print(f"\n⚔️  COMBAT START ⚔️")
    
    while any(e['hp'] > 0 for e in state['active_enemies'].values()) and state['hp'] > 0:
        alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
        
        print(f"\n--- 🛡️ YOUR TEAM: {state['name']} (HP: {state['hp']}/{state.get('max_hp', state['hp'])}) ---")
        for e_name, e_data in alive_enemies.items():
            max_hp = game_data['monsters'][e_data['type']]['hp']
            print(f"    🆚 {e_name} (HP: {e_data['hp']}/{max_hp})")
            
        # --- COMPANIONS ATTACK FIRST ---
        for comp in state.get('companions', []):
            alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
            if not alive_enemies: break
            
            target_name = random.choice(list(alive_enemies.keys()))
            if random.randint(1, 20) >= 10: # Flat 50% chance to hit
                c_dmg = random.randint(1, 6) # Base 1d6 damage
                state['active_enemies'][target_name]['hp'] -= c_dmg
                print(f"🤝 {comp} attacks {target_name} and hits! Deals {c_dmg} damage.")
                if state['active_enemies'][target_name]['hp'] <= 0:
                    print(f"💀 {target_name} has been defeated by {comp}!")
            else:
                print(f"💨 {comp} attacks {target_name} but misses!")

        # Re-check alive enemies after companion turn
        alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
        if not alive_enemies: break

        # --- PLAYER TURN ---
        c_action = input("\nCombat Action: [A]ttack, [S]kill/Spell, [U]se Item, [F]lee, or type a custom action (e.g., 'I throw sand at it'): ")
        
        if c_action.upper() == 'F':
            if random.randint(1, 20) > 10:
                print("\n[Success] You managed to run away!")
                state.pop('active_enemies', None)
                return True, "I successfully fled from the battle."
            else:
                print("\n[Failed] You couldn't escape!")
                
        elif c_action.upper() == 'A':
            target_name = list(alive_enemies.keys())[0]
            if len(alive_enemies) > 1:
                print("\nChoose your target:")
                target_list = list(alive_enemies.keys())
                for i, t_name in enumerate(target_list, 1):
                    print(f"{i}. {t_name}")
                try:
                    t_choice = int(input(f"Select target (1-{len(target_list)}): "))
                    if 1 <= t_choice <= len(target_list):
                        target_name = target_list[t_choice - 1]
                except ValueError:
                    print(f"Invalid choice. Auto-targeting {target_name}.")
            
            target_data = game_data['monsters'][alive_enemies[target_name]['type']]
            
            p_roll = random.randint(1, 20)
            wpn = state.get('equipped_weapon')
            wpn_name = wpn.lower() if wpn and wpn != 'None' else ''
            c_class = state.get('class', '').lower()
            
            str_mod = dice.get_modifier(state['stats']['STR'])
            dex_mod = dice.get_modifier(state['stats']['DEX'])
            int_mod = dice.get_modifier(state['stats']['INT'])
            wis_mod = dice.get_modifier(state['stats']['WIS'])
            cha_mod = dice.get_modifier(state['stats']['CHA'])
            
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
            
            print(f"\nYou rolled a {p_roll} + {combat_mod} ({stat_name} mod) + {prof_bonus} (Prof) = {p_total} to hit vs {target_name} (AC {target_data['ac']}).")
            
            if p_total >= target_data['ac']:
                desc = game_data.get('items', {}).get(wpn, {}).get('description', '1d4') if wpn else '1d4'
                dmg = max(1, dice.roll_from_string(desc) + combat_mod)
                state['active_enemies'][target_name]['hp'] -= dmg
                print(f"Hit! You deal {dmg} damage to {target_name} with your {wpn if wpn and wpn != 'None' else 'fists'}.")
                if state['active_enemies'][target_name]['hp'] <= 0:
                    print(f"💀 {target_name} has been defeated!")
            else:
                print("You missed!")
        elif c_action.upper() == 'S':
            if not state.get('spells'):
                print("You don't know any skills or spells!")
                continue
            print(f"\nMP: {state.get('mp', 0)}/{state.get('max_mp', 0)}")
            print("Known Skills/Spells:")
            for s in state['spells']:
                s_data = game_data.get('spells', {}).get(s, {})
                print(f"- {s} ({s_data.get('mp', 0)} MP): {s_data.get('description', 'Unknown effect')}")
            spell_choice = input("Enter skill/spell name to use (or Enter to cancel): ").title()
            if spell_choice not in state['spells']:
                continue
            spell_data = game_data.get('spells', {}).get(spell_choice)
            if not spell_data: continue
            if state.get('mp', 0) < spell_data.get('mp', 0):
                print("Not enough MP!")
                continue
            state['mp'] = state.get('mp', 0) - spell_data.get('mp', 0)
            
            if 'heal' in spell_data.get('description', '').lower():
                heal_amount = dice.roll_from_string(spell_data.get('description', ''), default_val=5)
                old_hp = state['hp']
                state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + heal_amount)
                print(f"\n✨ You use {spell_choice} and recover {state['hp'] - old_hp} HP! (Current HP: {state['hp']}/{state['max_hp']})")
                continue
                
            target_name = list(alive_enemies.keys())[0]
            if len(alive_enemies) > 1:
                print("\nChoose your target:")
                target_list = list(alive_enemies.keys())
                for i, t_name in enumerate(target_list, 1):
                    print(f"{i}. {t_name}")
                try:
                    t_choice = int(input(f"Select target (1-{len(target_list)}): "))
                    if 1 <= t_choice <= len(target_list):
                        target_name = target_list[t_choice - 1]
                except ValueError:
                    print(f"Invalid choice. Auto-targeting {target_name}.")
                    
            target_data = game_data['monsters'][alive_enemies[target_name]['type']]
            
            # Simple skill attack roll using highest mental stat (INT/WIS/CHA)
            int_mod, wis_mod, cha_mod = dice.get_modifier(state['stats']['INT']), dice.get_modifier(state['stats']['WIS']), dice.get_modifier(state['stats']['CHA'])
            spell_mod = max(int_mod, wis_mod, cha_mod)
            prof_bonus = 2 + ((state.get('level', 1) - 1) // 4)
            p_total = random.randint(1, 20) + spell_mod + prof_bonus
            
            print(f"\n✨ You use {spell_choice}! Attack Roll: {p_total - spell_mod - prof_bonus} + {spell_mod} (Stat mod) + {prof_bonus} (Prof) = {p_total} vs {target_name} (AC {target_data['ac']}).")
            
            if p_total >= target_data['ac']:
                dmg = max(1, dice.roll_from_string(spell_data.get('description', '1d4')))
                state['active_enemies'][target_name]['hp'] -= dmg
                print(f"Hit! 💥 {spell_choice} deals {dmg} damage to {target_name}.")
                if state['active_enemies'][target_name]['hp'] <= 0:
                    print(f"💀 {target_name} has been defeated!")
            else:
                print("The skill missed or was resisted!")
        elif c_action.upper() == 'U':
            if not actions.handle_use(state, game_data):
                continue
        elif len(c_action.strip()) > 1:
            print(f"\n[Handing over to the GM: '{c_action}']")
            return True, c_action
        else:
            print("Invalid action.")
            continue
                
        # --- ENEMY TURN ---
        alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
        for e_name, e_data in alive_enemies.items():
            if state['hp'] <= 0: break
            
            target_data = game_data['monsters'][e_data['type']]
            
            m_roll, m_hit_mod = random.randint(1, 20), 0
            m_atk_str = target_data.get('attack', '+0 to hit, 1d4 damage')
            if hit_match := re.search(r'\+(\d+)', m_atk_str): m_hit_mod = int(hit_match.group(1))
            m_total = m_roll + m_hit_mod
            
            # Choose Target (Player or Companions)
            targets = [state['name']] + state.get('companions', [])
            target = random.choice(targets)
            
            if target == state['name']:
                print(f"\n🩸 {e_name} attacks YOU! Rolls {m_roll} + {m_hit_mod} = {m_total} to hit vs your AC {state.get('ac', 10)}.")
                if m_total >= state.get('ac', 10):
                    # Isolate just the damage part of the attack string to pass to our parser
                    m_dmg = dice.roll_from_string(m_atk_str.split(',')[-1], default_val=random.randint(1, 4))
                    state['hp'] -= m_dmg
                    print(f"Ouch! {e_name} hits! You take {m_dmg} damage.")
                else: print(f"{e_name} misses you!")
            else:
                print(f"\n🩸 {e_name} attacks your companion, {target}!")
                if m_total >= 13: # Flat AC 13 for companions to keep it simple
                    print(f"Ouch! {e_name} hits {target}!")
                else:
                    print(f"{e_name} misses {target}!")

    if state['hp'] <= 0:
        return False, ""
        
    print(f"\n🎉 You defeated the enemies!")
    state.pop('active_enemies', None)
    return True, "I fought and killed the enemies."