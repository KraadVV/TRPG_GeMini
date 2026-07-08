import re
import cli_styles
import dice
from game_state import load_save, save_game, load_game_data, save_game_data
from gm_engine import generate_gm_response
import character
import combat
import actions
import skills
import conditions

def validate_monster_stats(stats):
    if not isinstance(stats, dict):
        return {"ac": 10, "hp": 10, "xp": 50, "attack": "+2 to hit, 1d6 damage", "dex": 10}
    
    try:
        ac = int(stats.get("ac", 10))
    except (TypeError, ValueError):
        ac = 10
    ac = max(5, min(25, ac))
    
    try:
        hp = int(stats.get("hp", 10))
    except (TypeError, ValueError):
        hp = 10
    hp = max(1, min(300, hp))
    
    try:
        xp = int(stats.get("xp", 50))
    except (TypeError, ValueError):
        xp = 50
    xp = max(0, min(5000, xp))
    
    try:
        dex = int(stats.get("dex", 10))
    except (TypeError, ValueError):
        dex = 10
    dex = max(1, min(30, dex))
    
    attack = str(stats.get("attack", "+2 to hit, 1d6 damage"))
    if not re.search(r'\+\d+', attack) or not re.search(r'\d+d\d+', attack):
        attack = "+2 to hit, 1d6 damage"
        
    return {
        "ac": ac,
        "hp": hp,
        "xp": xp,
        "attack": attack,
        "dex": dex
    }

def validate_spell_stats(stats):
    if not isinstance(stats, dict):
        return {"mp": 2, "description": "Deals 1d6 damage", "level": 1, "is_cantrip": False, "save_type": None, "concentration": False}
    
    try:
        mp = int(stats.get("mp", 2))
    except (TypeError, ValueError):
        mp = 2
    mp = max(0, min(50, mp))
    
    try:
        level = int(stats.get("level", 1))
    except (TypeError, ValueError):
        level = 1
    level = max(0, min(9, level))
    
    is_cantrip = bool(stats.get("is_cantrip", level == 0))
    
    save_type = stats.get("save_type")
    if save_type not in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        save_type = None
        
    concentration = bool(stats.get("concentration", False))
    
    description = str(stats.get("description", "Deals 1d6 damage"))
    return {
        "mp": mp,
        "description": description,
        "level": level,
        "is_cantrip": is_cantrip,
        "save_type": save_type,
        "concentration": concentration
    }

def main():
    cli_styles.draw_divider("═", 60, cli_styles.PURPLE)
    print(cli_styles.bold(cli_styles.cyan("         🎮 TRPG GeMini: AUTO-DM UPGRADED ENGINE 🎮")))
    cli_styles.draw_divider("═", 60, cli_styles.PURPLE)
    
    state = load_save()
    game_data = load_game_data()
    
    if not state:
        state = character.create_character()
        save_game(state)
    else:
        lang = state.get('language', 'Korean')
        welcome = f"\nWelcome back, {state['name']}! Resuming your adventure...\n"
        if lang == "Korean":
            welcome = f"\n다시 오신 것을 환영합니다, {state['name']} 님! 모험을 다시 시작합니다...\n"
        print(cli_styles.green(welcome))

    lang = state.get('language', 'Korean')
    if lang == "Korean":
        initial_action = "주변을 둘러보고 상황을 파악한다."
    else:
        initial_action = "Look around and assess the situation."
    
    while True:
        loading_msg = "[GM이 세계를 그리는 중...]" if lang == "Korean" else "[The GM is processing the world...]"
        print(cli_styles.gray(f"\n{loading_msg}\n"))
        
        try:
            # Generate Gemini GM Response
            gm_data = generate_gm_response(state, initial_action, game_data)
            
            # --- 1. STRICT LOCAL DETERMINISTIC RULE EXECUTION ---
            
            # Check Environmental Damage Dice
            if gm_data.get('damage_taken_dice'):
                dmg_expr = gm_data['damage_taken_dice']
                rolled_dmg = dice.roll_from_string(dmg_expr)
                state['hp'] = max(0, state['hp'] - rolled_dmg)
                
                trap_alert = f"⚠️ [위험] 함정이나 낙하로 인해 {rolled_dmg} 피해를 입었습니다! (주사위 식: {dmg_expr})" if lang == "Korean" else f"⚠️ [Hazard] You took {rolled_dmg} damage from the environment! (Dice: {dmg_expr})"
                print(cli_styles.red(f"\n{trap_alert}"))
                
                if state['hp'] <= 0:
                    dead_msg = "\n💀 전투 외 치명적인 상처로 쓰러졌습니다. 게임 오버." if lang == "Korean" else "\n💀 You have fallen to environmental damage. Game Over."
                    print(cli_styles.red(cli_styles.bold(dead_msg)))
                    return
            
            # Check Environmental Healing Dice
            if gm_data.get('heal_received_dice'):
                heal_expr = gm_data['heal_received_dice']
                rolled_heal = dice.roll_from_string(heal_expr)
                old_hp = state['hp']
                state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + rolled_heal)
                healed_val = state['hp'] - old_hp
                
                heal_alert = f"✨ [신비] 환경적 축복으로 {healed_val} HP를 회복했습니다! (주사위 식: {heal_expr})" if lang == "Korean" else f"✨ [Blessing] You recovered {healed_val} HP! (Dice: {heal_expr})"
                print(cli_styles.green(f"\n{heal_alert}"))
                
            # Check MP updates
            if gm_data.get('mp_used', 0) > 0 and state.get('max_mp', 0) > 0:
                mp_used = gm_data['mp_used']
                state['mp'] = max(0, state['mp'] - mp_used)
                mp_alert = f"🔵 마법 시전으로 {mp_used} MP를 소모했습니다." if lang == "Korean" else f"🔵 Consumed {mp_used} MP narratively."
                print(cli_styles.blue(mp_alert))
                
            if gm_data.get('mp_recovered', 0) > 0 and state.get('max_mp', 0) > 0:
                mp_rec = gm_data['mp_recovered']
                state['mp'] = min(state['max_mp'], state['mp'] + mp_rec)
                mp_alert = f"🔵 신비한 힘으로 {mp_rec} MP를 회복했습니다." if lang == "Korean" else f"🔵 Recovered {mp_rec} MP narratively."
                print(cli_styles.blue(mp_alert))

            # Sync player conditions from GM response
            if gm_data.get('player_conditions_add'):
                for cond in gm_data['player_conditions_add']:
                    if isinstance(cond, dict) and 'name' in cond:
                        conditions.add_condition(state, cond['name'], cond.get('duration'), cond.get('source'))
                        add_msg = f"⚠️ [상태 이상] {cond['name']} 상태가 부여되었습니다!" if lang == "Korean" else f"⚠️ [Condition] You gained condition: {cond['name']}!"
                        print(cli_styles.yellow(add_msg))

            if gm_data.get('player_conditions_remove'):
                for cond_name in gm_data['player_conditions_remove']:
                    conditions.remove_condition(state, cond_name)
                    rem_msg = f"✨ [상태 이상 해제] {cond_name} 상태가 치유되었습니다!" if lang == "Korean" else f"✨ [Condition Cleared] Cleared condition: {cond_name}!"
                    print(cli_styles.green(rem_msg))

            # Sync narrative properties
            state['inventory'] = gm_data['updated_inventory']
            state['location'] = gm_data['updated_location']
            state['can_shop'] = gm_data.get('can_shop', False)
            state['is_safe'] = gm_data.get('is_safe', False)
            state['companions'] = gm_data.get('updated_companions', state.get('companions', []))
            
            if 'updated_spells' in gm_data and gm_data['updated_spells'] is not None:
                state['spells'] = gm_data['updated_spells']
                
            # Level Up XP checks
            gained_xp = gm_data.get('awarded_xp', 0)
            character.check_level_up(state, gained_xp)
            
            # --- 2. RENDER THE BEAUTIFUL WORLD NARRATIVE ---
            
            # Stylized location header
            loc_label = "📍 현재 위치" if lang == "Korean" else "📍 Location"
            print(cli_styles.bold(cli_styles.cyan(f"\n{loc_label}: {state['location']}")))
            
            # Health / Mana HUD
            hp_bar = cli_styles.render_bar(state['hp'], state.get('max_hp', state['hp']), cli_styles.RED)
            hud_line = f"❤️ HP: {hp_bar}"
            if state.get('max_mp', 0) > 0:
                mp_bar = cli_styles.render_bar(state['mp'], state['max_mp'], cli_styles.BLUE)
                hud_line += f" | 🔵 MP: {mp_bar}"
            
            import skills_data
            next_lvl = state['level'] + 1
            threshold = skills_data.XP_THRESHOLDS.get(next_lvl, '???')
            hud_line += f" | ✨ XP: {state.get('xp', 0)}/{threshold}"
            
            active_conds = conditions.get_active_conditions(state)
            if active_conds:
                cond_str = ", ".join(active_conds)
                hud_line += f" | ⚠ Conditions: {cli_styles.yellow(cond_str)}"
            
            print(hud_line)
            if state.get('companions'):
                comp_label = "🤝 동료" if lang == "Korean" else "🤝 Companions"
                print(f"{comp_label}: {', '.join(state['companions'])}")
                
            cli_styles.draw_divider("─", 60, cli_styles.CYAN)
            
            # Narrative text Box
            cli_styles.draw_box("NARRATIVE", gm_data['narrative'], cli_styles.WHITE, cli_styles.WHITE)
            
            if gained_xp > 0:
                xp_msg = f"[성공적으로 난관을 극복하여 {gained_xp} XP를 획득했습니다!]" if lang == "Korean" else f"[You gained {gained_xp} XP!]"
                print(cli_styles.yellow(f"\n{xp_msg}"))
            cli_styles.draw_divider("─", 60, cli_styles.CYAN)
            
            # --- DYNAMIC MONSTER / SPELL CREATION REGISTER ---
            if gm_data.get('new_monsters_data'):
                if "monsters" not in game_data:
                    game_data["monsters"] = {}
                for m_name, m_stats in gm_data['new_monsters_data'].items():
                    game_data["monsters"][m_name] = validate_monster_stats(m_stats)
                    new_mon = f"📖 [도감 등록] 새로운 몬스터를 조우했습니다: {m_name}!" if lang == "Korean" else f"📖 [Bestiary Updated] The GM created a new monster: {m_name}!"
                    print(cli_styles.yellow(new_mon))
                save_game_data(game_data)
            
            if gm_data.get('new_spells_data'):
                if "spells" not in game_data:
                    game_data["spells"] = {}
                for s_name, s_stats in gm_data['new_spells_data'].items():
                    game_data["spells"][s_name] = validate_spell_stats(s_stats)
                    new_sp = f"✨ [스킬 습득] 새로운 비기를 전수받았습니다: {s_name}!" if lang == "Korean" else f"✨ [Skill Learned] Mastered a new ability: {s_name}!"
                    print(cli_styles.yellow(new_sp))
                save_game_data(game_data)
                
                if state.get('max_mp', 0) == 0:
                    state['max_mp'] = 10
                    state['mp'] = 10
                    mana_unlocked = "🔵 마법을 시전하기 위해 마나(MP) 통이 활성화되었습니다!" if lang == "Korean" else "🔵 Mana (MP) unlocked!"
                    print(cli_styles.blue(mana_unlocked))

            # --- COMBAT INTERCEPT ---
            if gm_data.get('situation_type') == 'combat_start' and gm_data.get('spawned_monsters'):
                survived, initial_action = combat.handle_combat(state, game_data, gm_data)
                if not survived:
                    dead_b = "\n💀 전투에서 전사하셨습니다. 게임 오버." if lang == "Korean" else "\n💀 YOU HAVE FALLEN IN BATTLE. Game Over."
                    print(cli_styles.red(cli_styles.bold(dead_b)))
                    return
                save_game(state)
                continue
                
            # --- SKILL CHECK INTERCEPT ---
            if gm_data.get('situation_type') == 'skill_check' and (gm_data.get('required_roll') or gm_data.get('required_skill')):
                initial_action = skills.handle_skill_check(state, gm_data)
                save_game(state)
                continue

            # --- 3. CHOICES MENU ---
            choice_title = "선택지" if lang == "Korean" else "GM CHOICES"
            cli_styles.draw_box(choice_title, [f"{i}. {choice}" for i, choice in enumerate(gm_data['choices'], 1)], cli_styles.YELLOW)
            
        except Exception as e:
            print(cli_styles.red(f"\n[API ERROR]: {e}"))
            break
        
        while True:
            if lang == "Korean":
                prompt_act = "\n무엇을 하시겠습니까? (1, 2, 3, 'status', 'equip', 'use', 'rest', 'shop', 'sell', 'quit' 혹은 자유 행동을 직접 기술하세요): "
            else:
                prompt_act = "\nWhat do you do? (1, 2, 3, 'status', 'equip', 'use', 'rest', 'shop', 'sell', 'quit', or custom action): "
                
            action = input(prompt_act).strip()
            
            if action.lower() == 'quit':
                exit_msg = "게임을 저장하고 종료합니다..." if lang == "Korean" else "Saving and exiting..."
                print(cli_styles.cyan(exit_msg))
                return
            
            if action.lower() in ['status', 'inventory', 'stats']:
                actions.show_status(state)
                continue
            
            if action.lower() == 'shop':
                if state.get('can_shop', False):
                    if actions.handle_shop(state, game_data): save_game(state)
                else:
                    no_shop = "\n[실패] 근처에 상인이나 거래소가 없습니다." if lang == "Korean" else "\n[Failed] There are no merchants nearby."
                    print(cli_styles.red(no_shop))
                continue

            if action.lower() == 'sell':
                if state.get('can_shop', False):
                    if actions.handle_sell(state, game_data): save_game(state)
                else:
                    no_shop = "\n[실패] 근처에 상인이나 거래소가 없습니다." if lang == "Korean" else "\n[Failed] There are no merchants nearby."
                    print(cli_styles.red(no_shop))
                continue
            
            if action.lower() == 'equip':
                if actions.handle_equip(state, game_data): save_game(state)
                continue
            
            if action.lower() == 'use':
                if actions.handle_use(state, game_data): save_game(state)
                continue
            
            if action.lower() == 'rest':
                if actions.handle_rest(state): save_game(state)
                continue
            
            # Map number shortcut to GM choice
            if action in ['1', '2', '3']:
                choice_idx = int(action) - 1
                choices = gm_data.get('choices', [])
                if 0 <= choice_idx < len(choices):
                    initial_action = choices[choice_idx]
                else:
                    initial_action = action
            else:
                initial_action = action
            
            break
            
        state["history"].append(initial_action)
        if len(state["history"]) > 5:
            state["history"].pop(0) 
            
        save_game(state)

if __name__ == "__main__":
    main()