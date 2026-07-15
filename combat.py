import random
import re
import actions
import dice
import cli_styles
import conditions

def heal_player(state, amount):
    """
    Heals the player, handles recovery from unconsciousness/stable status.
    """
    if amount <= 0:
        return
    old_hp = state['hp']
    state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + amount)
    
    # If the player was unconscious/rolling death saves and is healed
    if old_hp == 0 and state['hp'] > 0:
        conditions.remove_condition(state, 'unconscious')
        state['is_stable'] = False
        state.pop('death_saves', None)
        lang = state.get('language', 'Korean')
        msg = f"✨ 의식을 되찾고 일어났습니다!" if lang == "Korean" else f"✨ You have regained consciousness!"
        print(cli_styles.green(cli_styles.bold(msg)))

def damage_player(state, damage, is_crit=False):
    """
    Applies damage to the player, enforcing D&D 5e HP bounds, concentration checks,
    and death saving throw failures if the player is already unconscious.
    """
    if damage <= 0:
        return
        
    lang = state.get('language', 'Korean')
    
    # Concentration check
    if state.get('concentrating_on') and state['hp'] > 0:
        con_save_dc = max(10, damage // 2)
        # Roll CON saving throw
        success, total, detail = dice.make_saving_throw(state, 'CON', con_save_dc)
        if success:
            msg = f"🔆 집중 유지 성공! (CON 내성 굴림: {detail})" if lang == "Korean" else f"🔆 Concentration maintained! (CON Save: {detail})"
            print(cli_styles.green(msg))
        else:
            msg = f"🔆 집중이 깨졌습니다! (CON 내성 굴림: {detail})" if lang == "Korean" else f"🔆 Concentration broken! (CON Save: {detail})"
            print(cli_styles.red(msg))
            state['concentrating_on'] = None

    # Check if already at 0 HP (rolling death saves)
    if state['hp'] <= 0:
        # Damage at 0 HP is an automatic death save failure
        # Critical hits are 2 failures
        fail_count = 2 if is_crit else 1
        state.setdefault('death_saves', {'successes': 0, 'failures': 0})
        state['death_saves']['failures'] += fail_count
        msg = f"⚠ 의식불명 상태에서 피해를 입었습니다! 데스 세이브 실패 횟수 +{fail_count} (현재 실패: {state['death_saves']['failures']}/3)" if lang == "Korean" else f"⚠ Damage taken while unconscious! Death save failure +{fail_count} (Total failures: {state['death_saves']['failures']}/3)"
        print(cli_styles.red(cli_styles.bold(msg)))
        if state['death_saves']['failures'] >= 3:
            state['is_dead'] = True
            death_msg = "☠ 사망하였습니다..." if lang == "Korean" else "☠ You have died..."
            print(cli_styles.red(cli_styles.bold(death_msg)))
        return

    # Normal damage application
    old_hp = state['hp']
    state['hp'] -= damage
    
    # Check for instant death (massive damage)
    # If remaining damage after reducing to 0 HP is >= max_hp
    if state['hp'] <= 0:
        excess = abs(state['hp'])
        state['hp'] = 0
        
        # Unconscious condition
        conditions.add_condition(state, 'unconscious', duration=None)
        state['is_stable'] = False
        state['death_saves'] = {'successes': 0, 'failures': 0}
        
        # Drop concentration
        state['concentrating_on'] = None
        
        if excess >= state.get('max_hp', old_hp):
            state['is_dead'] = True
            msg = f"☠ 막대한 피해(Massive Damage, 초과 {excess})로 즉사하였습니다!" if lang == "Korean" else f"☠ You were instantly killed by Massive Damage (excess {excess})!"
            print(cli_styles.red(cli_styles.bold(msg)))
        else:
            msg = f"🩸 체력이 0이 되어 쓰러졌습니다! 의식을 잃었습니다." if lang == "Korean" else f"🩸 You fell to 0 HP and became unconscious!"
            print(cli_styles.red(cli_styles.bold(msg)))


def can_sneak_attack(state, wpn, has_adv, has_dis):
    """
    Checks if a Rogue can perform a Sneak Attack under D&D 5e rules.
    Requires: Rogue class, no sneak attack used yet this turn, no disadvantage,
    and a weapon that is Finesse (Dagger, Shortsword, Rapier) or Ranged (Bow, Crossbow).
    Also requires Advantage OR an ally/companion present.
    """
    if state.get('class') != 'Rogue':
        return False
    if state.get('sneak_attack_used_this_turn'):
        return False
    if has_dis:
        return False
        
    wpn_lower = wpn.lower() if wpn else ""
    is_finesse_or_ranged = False
    # Check for known finesse or ranged weapons
    if any(x in wpn_lower for x in ['dagger', 'shortsword', 'rapier', 'bow', 'crossbow']):
        is_finesse_or_ranged = True
        
    if not is_finesse_or_ranged:
        return False
        
    if has_adv or state.get('companions'):
        return True
        
    return False

def check_attack_advantage(attacker, target, is_ranged=False):
    """
    Determines if an attack has advantage or disadvantage based on conditions and armor penalty.
    """
    has_adv = False
    has_dis = False
    
    # Attacker conditions / penalties
    if attacker.get('armor_penalty'):
        has_dis = True
    if conditions.has_effect(attacker, 'attack_advantage'):
        has_adv = True
    if conditions.has_effect(attacker, 'attack_disadvantage'):
        has_dis = True
        
    # Target conditions
    if conditions.has_effect(target, 'attacked_advantage'):
        has_adv = True
    if conditions.has_effect(target, 'attacked_disadvantage'):
        has_dis = True
        
    # Prone target rules
    if conditions.has_condition(target, 'prone'):
        if is_ranged:
            has_dis = True
        else:
            has_adv = True
            
    return has_adv, has_dis

def get_spell_save_dc(state):
    """
    Calculates the player's spell save DC: 8 + prof + spellcasting modifier.
    """
    c_class = state.get('class', '').lower()
    int_mod = dice.get_modifier(state['stats']['INT'])
    wis_mod = dice.get_modifier(state['stats']['WIS'])
    cha_mod = dice.get_modifier(state['stats']['CHA'])
    
    spell_mod = int_mod
    if any(x in c_class for x in ['cleric', 'druid', 'ranger']):
        spell_mod = wis_mod
    elif any(x in c_class for x in ['bard', 'paladin', 'sorcerer', 'warlock']):
        spell_mod = cha_mod
        
    prof_bonus = 2 + ((state.get('level', 1) - 1) // 4)
    return 8 + prof_bonus + spell_mod

def get_damage_type(name, description=""):
    """
    4.5 Helper to detect damage type of weapons or spells.
    """
    name_l = name.lower()
    desc_l = description.lower()
    
    if 'sacred flame' in name_l: return 'radiant'
    if 'magic missile' in name_l: return 'force'
    
    for d_type in ['fire', 'cold', 'frost', 'lightning', 'acid', 'necrotic', 'radiant', 'force', 'poison', 'psychic', 'thunder']:
        if d_type in desc_l or d_type in name_l:
            return d_type
            
    if any(x in name_l for x in ['bow', 'crossbow', 'arrow', 'dagger', 'rapier', 'spear', 'piercing']):
        return 'piercing'
    if any(x in name_l for x in ['staff', 'club', 'hammer', 'mace', 'bludgeoning']):
        return 'bludgeoning'
    return 'slashing'

def apply_damage_mod(damage, damage_type, target_stats):
    """
    4.5 Apply resistances, immunities, and vulnerabilities.
    """
    resist = target_stats.get('damage_resistances', [])
    immune = target_stats.get('damage_immunities', [])
    vuln = target_stats.get('damage_vulnerabilities', [])
    
    if damage_type in immune:
        print(cli_styles.cyan(f"🛡️ Target is IMMUNE to {damage_type} damage! (0 damage)"))
        return 0
    elif damage_type in resist:
        dmg = damage // 2
        print(cli_styles.cyan(f"🛡️ Target is RESISTANT to {damage_type} damage! Halved to {dmg}."))
        return dmg
    elif damage_type in vuln:
        dmg = damage * 2
        print(cli_styles.yellow(f"💥 Target is VULNERABLE to {damage_type} damage! Doubled to {dmg}."))
        return dmg
    return damage

def handle_combat(state, game_data, gm_data):
    lang = state.get('language', 'Korean')
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
                "hp": game_data["monsters"][m_name]["hp"],
                "conditions": [],
                "reaction_used": False
            }
        if not active_enemies:
            return True, "The enemies fled before you could strike."
        state['active_enemies'] = active_enemies
        state['reaction_used'] = False
        
    # 4.6 Initialize Companion stats
    if 'companion_stats' not in state:
        state['companion_stats'] = {}
    for comp in state.get('companions', []):
        if comp not in state['companion_stats']:
            state['companion_stats'][comp] = {
                "hp": 15,
                "max_hp": 15,
                "ac": 13,
                "attack_bonus": 3,
                "damage": "1d6+2"
            }
        
    # Initialize surprise round if specified by the GM
    is_surprise = gm_data.get('is_surprise_round', False)
    surprised_side = gm_data.get('surprised_side')
    if is_surprise and not state.get('combat_surprise_processed'):
        state['combat_surprise_processed'] = True
        if surprised_side == 'enemies':
            for e_data in state['active_enemies'].values():
                e_data['surprised'] = True
        elif surprised_side == 'players':
            state['player_surprised'] = True
            state['companions_surprised'] = True

    # Print battle header
    battle_title = "⚔️ 전투 시작 ⚔️" if lang == "Korean" else "⚔️ COMBAT START ⚔️"
    surprise_msg = ""
    if is_surprise:
        surprise_msg = f"\n⚡ [SURPRISE ROUND] Surprised: {surprised_side}!"
    cli_styles.draw_box(battle_title, [
        "Dangerous enemies have drawn their weapons!",
        "적들이 무기를 뽑아 들고 습격해 옵니다!" if lang == "Korean" else "Prepare yourself for battle!" + surprise_msg
    ], cli_styles.RED)
    
    # 1.1 Initiative roll/load
    if not state.get('combat_initiative'):
        initiative_order = []
        # Player
        p_init = dice.roll_initiative(state['stats']['DEX'])
        initiative_order.append({"name": state['name'], "type": "player", "roll": p_init})
        # Companions
        for comp in state.get('companions', []):
            c_init = dice.roll_initiative(12)  # default 12 DEX
            initiative_order.append({"name": comp, "type": "companion", "roll": c_init})
        # Enemies
        for e_name, e_data in state['active_enemies'].items():
            e_type = e_data['type']
            e_dex = game_data['monsters'].get(e_type, {}).get('dex', 10)
            e_init = dice.roll_initiative(e_dex)
            initiative_order.append({"name": e_name, "type": "enemy", "roll": e_init})
            
        initiative_order.sort(key=lambda x: x['roll'], reverse=True)
        state['combat_initiative'] = initiative_order
        
        # Display Initiative
        init_lines = []
        for idx, actor in enumerate(initiative_order, 1):
            role = "Player" if actor['type'] == 'player' else ( "Companion" if actor['type'] == 'companion' else "Enemy" )
            init_lines.append(f"{idx}. {actor['name']} ({role}) - Initiative: {actor['roll']}")
        cli_styles.draw_box("🎲 Initiative Order 🎲", init_lines, cli_styles.PURPLE)

    while any(e['hp'] > 0 for e in state['active_enemies'].values()) and not state.get('is_dead', False):
        # Check if party is completely defeated
        player_down = state['hp'] <= 0
        all_companions_down = True
        for comp in state.get('companions', []):
            if state.get('companion_stats', {}).get(comp, {}).get('hp', 0) > 0:
                all_companions_down = False
                break
        if player_down and all_companions_down:
            break
            
        alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
        
        # Reset round-specific variables
        state['sneak_attack_used_this_turn'] = False
        
        # --- RENDER COMBAT ROUND HUD ---
        hud_lines = []
        player_hp_bar = cli_styles.render_bar(state['hp'], state.get('max_hp', state['hp']), cli_styles.RED)
        player_desc = f"{cli_styles.bold(state['name'])} (Lvl {state['level']} {state['class']})"
        
        p_conds = conditions.get_active_conditions(state)
        cond_suffix = f" | ⚠ {', '.join(p_conds)}" if p_conds else ""
        hud_lines.append(f"👤 {player_desc:<30} HP: {player_hp_bar}{cond_suffix}")
        
        # 4.6 Display Companion HUD with HP bars
        for comp in state.get('companions', []):
            c_stats = state.get('companion_stats', {}).get(comp, {"hp": 15, "max_hp": 15})
            comp_hp_bar = cli_styles.render_bar(c_stats['hp'], c_stats['max_hp'], cli_styles.GREEN)
            hud_lines.append(f"🤝 {comp:<30} HP: {comp_hp_bar}")
        
        # Phase 3 Show spell slots / MP
        spell_info = ""
        if state.get('use_spell_slots'):
            slots_list = []
            for sl_lvl, sl_max in state.get('spell_slots_max', {}).items():
                sl_curr = state.get('spell_slots', {}).get(str(sl_lvl), state.get('spell_slots', {}).get(sl_lvl, 0))
                slots_list.append(f"Lvl {sl_lvl}: {sl_curr}/{sl_max}")
            if slots_list:
                spell_info = "Slots: " + " | ".join(slots_list)
        else:
            if state.get('max_mp', 0) > 0:
                spell_info = f"MP: {state['mp']}/{state['max_mp']}"
                
        if state.get('concentrating_on'):
            spell_info += f" | 🔆 Conc: {state['concentrating_on']}"
            
        if spell_info:
            hud_lines.append(f"   {'':<30} {spell_info}")
            
        hud_lines.append(f"   {'-'*55}")
        
        for e_name, e_data in alive_enemies.items():
            max_hp = game_data['monsters'][e_data['type']]['hp']
            enemy_hp_bar = cli_styles.render_bar(e_data['hp'], max_hp, cli_styles.YELLOW)
            e_conds = conditions.get_active_conditions(e_data)
            e_cond_suffix = f" | ⚠ {', '.join(e_conds)}" if e_conds else ""
            hud_lines.append(f"🆚 {e_name:<30} HP: {enemy_hp_bar}{e_cond_suffix}")
            
        hud_title = "전투 상태" if lang == "Korean" else "COMBAT ROUND HUD"
        cli_styles.draw_box(hud_title, hud_lines, cli_styles.RED)
        
        # Execute turns in initiative order
        for actor in state['combat_initiative']:
            # Recheck survival
            alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
            player_down = state['hp'] <= 0
            all_companions_down = True
            for comp in state.get('companions', []):
                if state.get('companion_stats', {}).get(comp, {}).get('hp', 0) > 0:
                    all_companions_down = False
                    break
            if not alive_enemies or state.get('is_dead') or (player_down and all_companions_down):
                break
                
            actor_name = actor['name']
            actor_type = actor['type']
            
            # --- PLAYER TURN ---
            if actor_type == 'player':
                if state['hp'] <= 0:
                    if state.get('is_stable', False):
                        stable_msg = "\n🛌 당신은 안정된 상태(Stable)로 기절해 있습니다. 턴이 자동으로 넘어갑니다." if lang == "Korean" else "\n🛌 You are stable but unconscious. Skipping your turn."
                        print(cli_styles.cyan(stable_msg))
                        continue
                    
                    # Roll Death Saving Throw
                    title = "☠ 죽음 내성 굴림 (Death Saving Throw) ☠" if lang == "Korean" else "☠ Death Saving Throw ☠"
                    current_saves = state.setdefault('death_saves', {'successes': 0, 'failures': 0})
                    lines = [
                        "체력이 0이 되어 쓰러져 있습니다. 죽음의 문턱에서 저항해야 합니다!",
                        f"현재 상태 - 성공: {current_saves['successes']}/3, 실패: {current_saves['failures']}/3" if lang == "Korean" else f"Current Saves - Successes: {current_saves['successes']}/3, Failures: {current_saves['failures']}/3"
                    ]
                    cli_styles.draw_box(title, lines, cli_styles.RED)
                    
                    roll_prompt = "엔터를 눌러 죽음 내성 굴림(d20)을 수행하세요..." if lang == "Korean" else "Press Enter to roll a Death Saving Throw (d20)..."
                    input(roll_prompt)
                    
                    roll_result = random.randint(1, 20)
                    if roll_result == 20:
                        state['hp'] = 1
                        state.pop('death_saves', None)
                        state['is_stable'] = False
                        conditions.remove_condition(state, 'unconscious')
                        msg = f"✨ 기적! 자연 20(Natural 20)을 굴려 1 HP로 의식을 되찾았습니다!" if lang == "Korean" else f"✨ Miracle! Rolled a Natural 20, regaining consciousness with 1 HP!"
                        print(cli_styles.green(cli_styles.bold(msg)))
                        # Let them proceed to take their turn normally!
                    elif roll_result == 1:
                        state['death_saves']['failures'] += 2
                        msg = f"⚠️ 자연 1(Natural 1)을 굴려 데스 세이브 2회 실패! (누적 실패: {state['death_saves']['failures']}/3)" if lang == "Korean" else f"⚠️ Critical failure! Rolled a Natural 1: 2 death save failures! (Total failures: {state['death_saves']['failures']}/3)"
                        print(cli_styles.red(cli_styles.bold(msg)))
                    elif roll_result >= 10:
                        state['death_saves']['successes'] += 1
                        msg = f"✅ 성공! ({roll_result}) (누적 성공: {state['death_saves']['successes']}/3)" if lang == "Korean" else f"✅ Success! ({roll_result}) (Total successes: {state['death_saves']['successes']}/3)"
                        print(cli_styles.green(msg))
                    else:
                        state['death_saves']['failures'] += 1
                        msg = f"❌ 실패... ({roll_result}) (누적 실패: {state['death_saves']['failures']}/3)" if lang == "Korean" else f"❌ Failure... ({roll_result}) (Total failures: {state['death_saves']['failures']}/3)"
                        print(cli_styles.red(msg))
                        
                    # Check death/stable conditions
                    if state['death_saves']['failures'] >= 3:
                        state['is_dead'] = True
                        print(cli_styles.red(cli_styles.bold("\n☠ 결국 사망에 이르렀습니다...")))
                        break
                    elif state['death_saves']['successes'] >= 3:
                        state['is_stable'] = True
                        state.pop('death_saves', None)
                        print(cli_styles.cyan(cli_styles.bold("\n🛌 상태가 안정(Stable)되었습니다. 더 이상 내성 굴림을 굴리지 않지만, 여전히 의식 불명 상태입니다.")))
                        
                    if roll_result != 20:
                        continue # Skip normal action choices if not waking up
                
                if state.get('player_surprised'):
                    print(cli_styles.yellow(f"\n⚡ {actor_name} is surprised and skips their turn!"))
                    state['player_surprised'] = False
                    continue
                    
                if not conditions.can_act(state):
                    p_conds = conditions.get_active_conditions(state)
                    print(cli_styles.red(f"\n⚠️ {actor_name} is incapacitated ({', '.join(p_conds)}) and cannot act!"))
                    continue
                
                # 4.1 Action Economy Tracking
                action_used = False
                bonus_action_used = False
                state['cover_ac_bonus'] = 0 # Reset cover AC bonus at turn start
                
                # Input Action loop
                while not (action_used and bonus_action_used):
                    # Recheck enemies
                    alive_enemies = {name: data for name, data in state['active_enemies'].items() if data['hp'] > 0}
                    if not alive_enemies or state['hp'] <= 0:
                        break
                        
                    res_lines = []
                    if not action_used: res_lines.append("[Action]")
                    if not bonus_action_used: res_lines.append("[Bonus Action]")
                    res_msg = f" (Resources: {', '.join(res_lines)})" if res_lines else ""
                    
                    if lang == "Korean":
                        prompt = f"\n행동 선택{res_msg}: [A]공격, [S]스킬/마법, [U]아이템 사용, [C]엄폐(Cover), [F]도주, [E]턴 종료: "
                    else:
                        prompt = f"\nCombat Action{res_msg}: [A]ttack, [S]kill/Spell, [U]se Item, [C]over, [F]lee, [E]nd Turn: "
                        
                    c_action = input(prompt).strip()
                    
                    if c_action.upper() == 'E':
                        break
                        
                    elif c_action.upper() == 'C':
                        # 4.8 Cover System
                        if action_used:
                            print(cli_styles.red("\n❌ Action already used! / 이미 액션을 소비했습니다!"))
                            continue
                        
                        print("\n🛡️ 엄폐물 뒤로 숨어 방어도를 높입니다!")
                        state['cover_ac_bonus'] = 2 # +2 AC cover
                        action_used = True
                        
                    elif c_action.upper() == 'F':
                        if action_used:
                            print(cli_styles.red("\n❌ Action already used! / 이미 액션을 소비했습니다!"))
                            continue
                            
                        # 1.4 Opportunity Attacks on Flee
                        print("\n⚡ 도주 시도! 적들의 기회 공격(Opportunity Attack)이 발생합니다!")
                        for enemy_name, enemy_data in alive_enemies.items():
                            if enemy_data['hp'] > 0 and not enemy_data.get('reaction_used') and conditions.can_act(enemy_data):
                                enemy_data['reaction_used'] = True
                                monster_type = enemy_data['type']
                                monster_stats = game_data['monsters'][monster_type]
                                m_atk_str = monster_stats.get('attack', '+0 to hit, 1d4 damage')
                                m_hit_mod = 0
                                if hit_match := re.search(r'\+(\d+)', m_atk_str):
                                    m_hit_mod = int(hit_match.group(1))
                                
                                is_ranged = 'bow' in m_atk_str.lower() or 'crossbow' in m_atk_str.lower()
                                enemy_adv, enemy_dis = check_attack_advantage(enemy_data, state, is_ranged)
                                m_roll, m_detail = dice.roll_d20(advantage=enemy_adv, disadvantage=enemy_dis)
                                m_total = m_roll + m_hit_mod
                                
                                print(f"🗡️ {enemy_name}의 기회 공격: d20({m_detail}) + {m_hit_mod} = {m_total} vs AC {state.get('ac', 10)}")
                                if m_total >= state.get('ac', 10):
                                    m_dmg = dice.roll_from_string(m_atk_str.split(',')[-1], default_val=random.randint(1, 4))
                                    damage_player(state, m_dmg, is_crit=(m_roll == 20))
                                    print(cli_styles.red(f"💥 맞았습니다! {m_dmg} 피해! (남은 HP: {state['hp']})"))
                                else:
                                    print(cli_styles.gray(f"💨 빗나갔습니다!"))
                                
                                if state.get('is_dead') or state['hp'] <= 0:
                                    break
                                    
                        if state.get('is_dead'):
                            return False, ""
                            
                        # Flee Roll
                        flee_roll = random.randint(1, 20)
                        if flee_roll > 10:
                            success_flee = "도주에 성공했습니다!" if lang == "Korean" else "I successfully fled from the battle."
                            print(cli_styles.green(f"\n[Success] {success_flee}"))
                            # Clear Combat States
                            state.pop('active_enemies', None)
                            state.pop('combat_initiative', None)
                            state.pop('combat_surprise_processed', None)
                            state.pop('player_surprised', None)
                            state.pop('companions_surprised', None)
                            state.pop('sneak_attack_used_this_turn', None)
                            state.pop('cover_ac_bonus', None)
                            return True, success_flee
                        else:
                            fail_flee = "도주에 실패했습니다! 적들이 길을 막습니다." if lang == "Korean" else "You couldn't escape!"
                            print(cli_styles.red(f"\n[Failed] {fail_flee}"))
                            action_used = True
                            
                    elif c_action.upper() == 'A':
                        if action_used:
                            print(cli_styles.red("\n❌ Action already used! / 이미 액션을 소비했습니다!"))
                            continue
                            
                        target_name = list(alive_enemies.keys())[0]
                        if len(alive_enemies) > 1:
                            title_choice = "공격 대상 선택" if lang == "Korean" else "Choose Target"
                            choices_lines = []
                            target_list = list(alive_enemies.keys())
                            for i, t_name in enumerate(target_list, 1):
                                choices_lines.append(f"{i}. {t_name}")
                            cli_styles.draw_box(title_choice, choices_lines, cli_styles.YELLOW)
                            
                            try:
                                prompt_sel = "대상을 선택하세요: " if lang == "Korean" else "Select target: "
                                t_choice = int(input(prompt_sel))
                                if 1 <= t_choice <= len(target_list):
                                    target_name = target_list[t_choice - 1]
                            except ValueError:
                                print(f"Invalid target. Auto-targeting {target_name}.")
                        
                        target_enemy_data = state['active_enemies'][target_name]
                        target_stats = game_data['monsters'][target_enemy_data['type']]
                        
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
                        
                        is_ranged = any(x in wpn_name for x in ['bow', 'crossbow', 'sling', 'dart'])
                        if is_ranged:
                            combat_mod, stat_name = dex_mod, "DEX"
                        elif any(x in wpn_name for x in ['dagger', 'rapier', 'shortsword', 'whip']):
                            combat_mod, stat_name = (dex_mod, "DEX") if dex_mod > str_mod else (str_mod, "STR")
                        elif any(x in wpn_name for x in ['staff', 'wand', 'tome']) or (not wpn_name and any(x in c_class for x in ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard'])):
                            combat_mod, stat_name = spell_mod, spell_stat
                        else:
                            combat_mod, stat_name = str_mod, "STR"
                            
                        prof_bonus = 2 + ((state.get('level', 1) - 1) // 4)
                        
                        # 1.2 Advantage/Disadvantage
                        has_adv, has_dis = check_attack_advantage(state, target_enemy_data, is_ranged)
                        p_roll, roll_detail = dice.roll_d20(advantage=has_adv, disadvantage=has_dis)
                        
                        # 2.5 Halfling Lucky Reroll
                        if p_roll == 1 and 'Lucky' in state.get('racial_traits', []):
                            p_roll = random.randint(1, 20)
                            roll_detail += f" -> Lucky Reroll: d20({p_roll})"
                            
                        p_total = p_roll + combat_mod + prof_bonus
                        
                        roll_log = f"🎲 Roll: {cli_styles.yellow(roll_detail)} + {cli_styles.cyan(f'{combat_mod} ({stat_name})')} + {cli_styles.purple(f'{prof_bonus} (Prof)')} = {cli_styles.bold(str(p_total))} vs {target_name} (AC {target_stats['ac']})"
                        print(f"\n{roll_log}")
                        
                        # Automatic Critical Hits on paralyzed/unconscious targets
                        is_crit = (p_roll == 20) or (p_total >= target_stats['ac'] and not is_ranged and conditions.has_effect(target_enemy_data, 'melee_auto_crit'))
                        
                        if is_crit:
                            crit_label = "💥 AUTOMATIC CRITICAL HIT!" if p_roll != 20 else "💥 CRITICAL HIT!"
                            print(cli_styles.green(cli_styles.bold(f"{crit_label} Double damage rolls!")))
                            desc = game_data.get('items', {}).get(wpn, {}).get('description', '1d4') if wpn else '1d4'
                            dmg = dice.roll_from_string(desc) + dice.roll_from_string(desc) + combat_mod
                            
                            # 2.5 Orc Savage Attacks melee crit bonus
                            if not is_ranged and 'Savage Attacks' in state.get('racial_traits', []):
                                extra_die = dice.roll_from_string(desc.split('+')[0], default_val=4)
                                dmg += extra_die
                                print(cli_styles.green(f"💀 Savage Attacks: Critical deals +{extra_die} extra damage!"))
                                
                            # 2.6 Rogue Sneak Attack
                            if can_sneak_attack(state, wpn, has_adv, has_dis):
                                sa_dice = f"{2 * ((state['level'] + 1) // 2)}d6"
                                sa_dmg = dice.roll_from_string(sa_dice)
                                dmg += sa_dmg
                                state['sneak_attack_used_this_turn'] = True
                                print(cli_styles.green(f"🗡️ Sneak Attack! Deals +{sa_dmg} ({sa_dice}) [CRIT DOUBLE] damage!"))
                                    
                            dmg = max(1, dmg)
                            
                            # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                            dmg_type = get_damage_type(wpn if wpn else "unarmed")
                            dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                            
                            target_enemy_data['hp'] -= dmg
                            hit_msg = f"명중! {wpn if wpn else '맨손'}으로 {target_name}에게 {dmg}의 치명타 물리 피해를 가했습니다!" if lang == "Korean" else f"Critical Hit! You deal {dmg} damage to {target_name}."
                            print(cli_styles.green(hit_msg))
                        elif p_roll == 1:
                            print(cli_styles.red("[Critical Miss] You fumbled and completely missed your target!"))
                        elif p_total >= target_stats['ac']:
                            desc = game_data.get('items', {}).get(wpn, {}).get('description', '1d4') if wpn else '1d4'
                            dmg = dice.roll_from_string(desc) + combat_mod
                            
                            # 2.6 Rogue Sneak Attack
                            if can_sneak_attack(state, wpn, has_adv, has_dis):
                                sa_dice = f"{(state['level'] + 1) // 2}d6"
                                sa_dmg = dice.roll_from_string(sa_dice)
                                dmg += sa_dmg
                                state['sneak_attack_used_this_turn'] = True
                                print(cli_styles.green(f"🗡️ Sneak Attack! Deals +{sa_dmg} ({sa_dice}) damage!"))
                                    
                            dmg = max(1, dmg)
                            
                            # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                            dmg_type = get_damage_type(wpn if wpn else "unarmed")
                            dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                            
                            target_enemy_data['hp'] -= dmg
                            
                            hit_msg = f"명중! {wpn if wpn else '맨손'}으로 {target_name}에게 {dmg}의 물리 피해를 가했습니다!" if lang == "Korean" else f"Hit! You deal {dmg} damage to {target_name}."
                            print(cli_styles.green(hit_msg))
                        else:
                            miss_msg = "공격이 빗나갔습니다!" if lang == "Korean" else "You missed!"
                            print(cli_styles.gray(miss_msg))
                            
                        if target_enemy_data['hp'] <= 0:
                            defeat_msg = f"💀 {target_name}이(가) 쓰러졌습니다!" if lang == "Korean" else f"💀 {target_name} has been defeated!"
                            print(cli_styles.red(defeat_msg))
                        action_used = True
                        
                    elif c_action.upper() == 'S':
                        if not state.get('spells'):
                            no_spells = "배운 스킬이나 마법이 없습니다!" if lang == "Korean" else "You don't know any skills or spells!"
                            print(cli_styles.red(f"\n{no_spells}"))
                            continue
                            
                        spell_list_title = "사용 가능한 스킬/마법" if lang == "Korean" else "Known Skills/Spells"
                        spell_lines = []
                        
                        # Add Second Wind details if Fighter
                        fw_wind = state.get('class_features', {}).get('Second Wind')
                        if fw_wind:
                            spell_lines.append(f"- Second Wind ({fw_wind.get('uses_remaining')}/{fw_wind.get('max_uses')} Remaining)")
                            
                        for s in state['spells']:
                            if s == 'Second Wind': continue
                            s_data = game_data.get('spells', {}).get(s, {})
                            is_cantrip = s_data.get('is_cantrip', False) or s_data.get('level', 1) == 0
                            cost_label = "Cantrip" if is_cantrip else (f"Lvl {s_data.get('level', 1)}" if state.get('use_spell_slots') else f"{s_data.get('mp', 0)} MP")
                            spell_lines.append(f"- {cli_styles.cyan(s)} ({cost_label}): {s_data.get('description', 'Unknown')}")
                            
                        cli_styles.draw_box(spell_list_title, spell_lines, cli_styles.BLUE)
                        
                        prompt_sp = "시전할 스킬/마법 이름을 입력하세요 (취소하려면 엔터): " if lang == "Korean" else "Enter skill/spell name to use (or Enter to cancel): "
                        spell_choice = input(prompt_sp).strip().title()
                        
                        if spell_choice not in state['spells']:
                            continue
                            
                        # 2.6 Fighter Second Wind (Bonus Action)
                        if spell_choice == "Second Wind":
                            if bonus_action_used:
                                print(cli_styles.red("\n❌ Bonus Action already used! / 이미 보너스 액션을 소비했습니다!"))
                                continue
                                
                            feat_state = state.get('class_features', {}).get('Second Wind')
                            if feat_state and feat_state.get('uses_remaining', 0) <= 0:
                                print(cli_styles.red("\nYou have already used Second Wind! It recovers on a rest."))
                                continue
                                
                            if feat_state:
                                feat_state['uses_remaining'] -= 1
                                
                            heal_roll = random.randint(1, 10)
                            heal_amount = heal_roll + state['level']
                            old_hp = state['hp']
                            heal_player(state, heal_amount)
                            
                            print(cli_styles.green(f"\n💨 Second Wind! Recovered {state['hp'] - old_hp} HP (1d10({heal_roll}) + Fighter level {state['level']})."))
                            bonus_action_used = True
                            continue
                            
                        # 2.6 Fighter Action Surge (Special Free Action)
                        if spell_choice == "Action Surge":
                            feat_state = state.get('class_features', {}).get('Action Surge')
                            if feat_state and feat_state.get('uses_remaining', 0) <= 0:
                                print(cli_styles.red("\nYou have already used Action Surge! It recovers on a rest."))
                                continue
                                
                            if feat_state:
                                feat_state['uses_remaining'] -= 1
                                
                            action_used = False # Reset action_used so they get another action!
                            print(cli_styles.green("\n⚡ Action Surge! You have gained an additional action this turn! / 추가 액션을 획득했습니다!"))
                            continue
                            
                        # Standard spells consume Action
                        if action_used:
                            print(cli_styles.red("\n❌ Action already used! / 이미 액션을 소비했습니다!"))
                            continue
                            
                        # 4.2 Spellcasting armor penalty check
                        if state.get('armor_penalty'):
                            print(cli_styles.red("\n❌ You cannot cast spells while wearing armor you are not proficient with!"))
                            continue
                            
                        spell_data = game_data.get('spells', {}).get(spell_choice)
                        if not spell_data: continue
                        
                        # 3.3 Cantrips & 3.1 Spell Slots vs MP
                        is_cantrip = spell_data.get('is_cantrip', False) or spell_data.get('level', 1) == 0
                        spell_level = spell_data.get('level', 1)
                        
                        if not is_cantrip:
                            if state.get('use_spell_slots'):
                                s_key = str(spell_level) if str(spell_level) in state.get('spell_slots', {}) else spell_level
                                if state.get('spell_slots', {}).get(s_key, 0) <= 0:
                                    print(cli_styles.red(f"\nNo level {spell_level} spell slots remaining! / 주문 슬롯이 부족합니다!"))
                                    continue
                                state['spell_slots'][s_key] -= 1
                            else:
                                mp_cost = spell_data.get('mp', 0)
                                if state.get('mp', 0) < mp_cost:
                                    print(cli_styles.red("\nNot enough MP! / 마나가 부족합니다!"))
                                    continue
                                state['mp'] = state.get('mp', 0) - mp_cost
                        
                        # Handle Healing Spell
                        if 'heal' in spell_data.get('description', '').lower():
                            heal_amount = dice.roll_from_string(spell_data.get('description', ''), default_val=5)
                            old_hp = state['hp']
                            state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + heal_amount)
                            
                            heal_msg = f"✨ {spell_choice}을(를) 시전하여 {state['hp'] - old_hp} HP를 회복했습니다!" if lang == "Korean" else f"✨ You use {spell_choice} and recover {state['hp'] - old_hp} HP!"
                            print(cli_styles.green(f"\n{heal_msg} (HP: {state['hp']}/{state['max_hp']})"))
                            action_used = True
                            break
                            
                        # Select Target for Attack Spells
                        target_name = list(alive_enemies.keys())[0]
                        if len(alive_enemies) > 1:
                            title_choice = "공격 대상 선택" if lang == "Korean" else "Choose Target"
                            choices_lines = []
                            target_list = list(alive_enemies.keys())
                            for i, t_name in enumerate(target_list, 1):
                                choices_lines.append(f"{i}. {t_name}")
                            cli_styles.draw_box(title_choice, choices_lines, cli_styles.YELLOW)
                            try:
                                prompt_sel = "대상을 선택하세요: " if lang == "Korean" else "Select target: "
                                t_choice = int(input(prompt_sel))
                                if 1 <= t_choice <= len(target_list):
                                    target_name = target_list[t_choice - 1]
                            except ValueError:
                                print(f"Invalid target. Auto-targeting {target_name}.")
                                
                        target_enemy_data = state['active_enemies'][target_name]
                        target_stats = game_data['monsters'][target_enemy_data['type']]
                        
                        # 3.4 Handle Spell Concentration
                        if spell_data.get('concentration', False):
                            if state.get('concentrating_on') and state['concentrating_on'] != spell_choice:
                                print(cli_styles.yellow(f"🔆 Ending concentration on {state['concentrating_on']}."))
                            state['concentrating_on'] = spell_choice
                            print(cli_styles.green(f"🔆 You are now concentrating on {spell_choice}."))
                        
                        # 3.2 Saving Throw based spells
                        save_type = spell_data.get('save_type')
                        if save_type:
                            dc = get_spell_save_dc(state)
                            
                            # Construct temp state for target saving throw
                            target_temp = {
                                "stats": {
                                    "STR": target_stats.get("str", 10),
                                    "DEX": target_stats.get("dex", 10),
                                    "CON": target_stats.get("con", 10),
                                    "INT": target_stats.get("int", 10),
                                    "WIS": target_stats.get("wis", 10),
                                    "CHA": target_stats.get("cha", 10),
                                },
                                "level": 1,
                                "save_proficiencies": [],
                                "conditions": target_enemy_data.get("conditions", [])
                            }
                            
                            # Apply Prone / Restrained disadvantages
                            m_adv = False
                            m_dis = False
                            if save_type == 'DEX' and conditions.has_effect(target_enemy_data, 'dex_save_disadvantage'):
                                m_dis = True
                                
                            success, s_total, s_detail = dice.make_saving_throw(target_temp, save_type, dc, advantage=m_adv, disadvantage=m_dis)
                            
                            print(f"\n✨ {spell_choice} (Save DC {dc}): {target_name} rolls {save_type} Saving Throw -> {s_detail}")
                            
                            if success:
                                if spell_choice.lower() == 'sacred flame':
                                    dmg = 0
                                    print(cli_styles.gray(f"💨 {target_name} succeeded the save. Sacred Flame deals 0 damage."))
                                else:
                                    desc = spell_data.get('description', '1d4')
                                    dmg = max(1, dice.roll_from_string(desc) // 2)
                                    
                                    # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                                    dmg_type = get_damage_type(spell_choice, spell_data.get('description', ''))
                                    dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                                    
                                    target_enemy_data['hp'] -= dmg
                                    print(cli_styles.green(f"Hit! {target_name} saved and takes half damage: {dmg}."))
                            else:
                                desc = spell_data.get('description', '1d4')
                                dmg = max(1, dice.roll_from_string(desc))
                                
                                # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                                dmg_type = get_damage_type(spell_choice, spell_data.get('description', ''))
                                dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                                
                                target_enemy_data['hp'] -= dmg
                                print(cli_styles.red(f"💥 Failed! {target_name} takes full damage: {dmg}."))
                        else:
                            # 5e Magic Missile Auto-Hit rule
                            is_magic_missile = 'magic missile' in spell_choice.lower()
                            
                            if is_magic_missile:
                                desc = spell_data.get('description', '3d4+3')
                                dmg = max(1, dice.roll_from_string(desc))
                                
                                # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                                dmg_type = get_damage_type(spell_choice, spell_data.get('description', ''))
                                dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                                
                                target_enemy_data['hp'] -= dmg
                                print(cli_styles.green(f"\n✨ Magic Missile automatically hits! Deals {dmg} force damage to {target_name}."))
                            else:
                                # Normal Spell Attack Roll
                                int_mod = dice.get_modifier(state['stats']['INT'])
                                wis_mod = dice.get_modifier(state['stats']['WIS'])
                                cha_mod = dice.get_modifier(state['stats']['CHA'])
                                spell_mod = max(int_mod, wis_mod, cha_mod)
                                prof_bonus = 2 + ((state.get('level', 1) - 1) // 4)
                                
                                has_adv, has_dis = check_attack_advantage(state, target_enemy_data, is_ranged=True)
                                p_roll, roll_detail = dice.roll_d20(advantage=has_adv, disadvantage=has_dis)
                                
                                if p_roll == 1 and 'Lucky' in state.get('racial_traits', []):
                                    p_roll = random.randint(1, 20)
                                    roll_detail += f" -> Lucky Reroll: d20({p_roll})"
                                    
                                p_total = p_roll + spell_mod + prof_bonus
                                
                                roll_log = f"✨ Roll: {cli_styles.yellow(roll_detail)} + {cli_styles.cyan(f'{spell_mod} (Spell mod)')} + {cli_styles.purple(f'{prof_bonus} (Prof)')} = {cli_styles.bold(str(p_total))} vs {target_name} (AC {target_stats['ac']})"
                                print(f"\n{roll_log}")
                                
                                is_crit = (p_roll == 20) or (p_total >= target_stats['ac'] and conditions.has_effect(target_enemy_data, 'melee_auto_crit'))
                                
                                if is_crit:
                                    print(cli_styles.green(cli_styles.bold("💥 CRITICAL HIT! Spell critical double damage!")))
                                    desc = spell_data.get('description', '1d4')
                                    dmg = dice.roll_from_string(desc) + dice.roll_from_string(desc)
                                    

                                            
                                    dmg = max(1, dmg)
                                    
                                    # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                                    dmg_type = get_damage_type(spell_choice, spell_data.get('description', ''))
                                    dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                                    
                                    target_enemy_data['hp'] -= dmg
                                    hit_msg = f"치명타! 💥 {spell_choice} 마법이 폭발하며 {target_name}에게 {dmg}의 강력한 마법 피해를 주었습니다!" if lang == "Korean" else f"Critical hit! 💥 {spell_choice} deals {dmg} damage to {target_name}."
                                    print(cli_styles.green(hit_msg))
                                elif p_roll == 1:
                                    print(cli_styles.red("[Critical Miss] The spell fizzles and goes wild!"))
                                elif p_total >= target_stats['ac']:
                                    dmg = dice.roll_from_string(spell_data.get('description', '1d4'))
                                    

                                            
                                    dmg = max(1, dmg)
                                    
                                    # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                                    dmg_type = get_damage_type(spell_choice, spell_data.get('description', ''))
                                    dmg = apply_damage_mod(dmg, dmg_type, target_stats)
                                    
                                    target_enemy_data['hp'] -= dmg
                                    hit_msg = f"명중! 💥 {spell_choice} 마법이 {target_name}에게 {dmg}의 마법 피해를 입혔습니다!" if lang == "Korean" else f"Hit! 💥 {spell_choice} deals {dmg} damage to {target_name}."
                                    print(cli_styles.green(hit_msg))
                                else:
                                    miss_msg = "마법이 저항되거나 빗나갔습니다!" if lang == "Korean" else "The spell was resisted or missed!"
                                    print(cli_styles.gray(miss_msg))
                        action_used = True
                        break
                        
                    elif c_action.upper() == 'U':
                        if action_used:
                            print(cli_styles.red("\n❌ Action already used! / 이미 액션을 소비했습니다!"))
                            continue
                        if actions.handle_use(state, game_data):
                            action_used = True
                            break
                    else:
                        print("Invalid combat action.")
                
            # --- COMPANION TURN ---
            elif actor_type == 'companion':
                if state.get('companions_surprised'):
                    # Handled silently; cleared at round end
                    continue
                    
                # 4.6 Companion HP/death state check
                comp_stats = state.get('companion_stats', {}).get(actor_name, {"hp": 15, "max_hp": 15, "ac": 13, "attack_bonus": 3, "damage": "1d6+2"})
                if comp_stats['hp'] <= 0:
                    print(cli_styles.red(f"\n🤝 동료 {actor_name}은(는) 쓰러져 있어서 행동할 수 없습니다!"))
                    continue
                    
                target_name = random.choice(list(alive_enemies.keys()))
                target_enemy_data = state['active_enemies'][target_name]
                target_stats = game_data['monsters'][target_enemy_data['type']]
                
                # Companion Attack Roll
                comp_adv, comp_dis = check_attack_advantage({}, target_enemy_data, is_ranged=False)
                
                c_roll, roll_detail = dice.roll_d20(advantage=comp_adv, disadvantage=comp_dis)
                c_total = c_roll + comp_stats['attack_bonus']
                
                is_crit = (c_roll == 20)
                if is_crit or (c_total >= target_stats['ac'] and c_roll != 1):
                    damage_formula = comp_stats.get('damage', '1d6+2')
                    if is_crit:
                        print(cli_styles.green(cli_styles.bold("💥 CRITICAL HIT! Companion attack critical double damage!")))
                        c_dmg = dice.roll_from_string(damage_formula) + dice.roll_from_string(damage_formula)
                    else:
                        c_dmg = dice.roll_from_string(damage_formula)
                    
                    # 4.5 Apply Damage Resistance/Vulnerability/Immunity
                    dmg_type = get_damage_type("companion attack")
                    c_dmg = apply_damage_mod(c_dmg, dmg_type, target_stats)
                    
                    target_enemy_data['hp'] -= c_dmg
                    
                    msg = f"🤝 동료 {actor_name}이(가) {target_name}을(를) 공격하여 명중시켰습니다! {c_dmg} 피해." if lang == "Korean" else f"🤝 {actor_name} attacks {target_name} and hits! Deals {c_dmg} damage."
                    print(cli_styles.green(msg))
                    
                    if target_enemy_data['hp'] <= 0:
                        defeat_msg = f"💀 {target_name}이(가) {actor_name}에 의해 쓰러졌습니다!" if lang == "Korean" else f"💀 {target_name} has been defeated by {actor_name}!"
                        print(cli_styles.red(defeat_msg))
                else:
                    miss_msg = f"💨 {actor_name}이(가) {target_name}을(를) 공격했으나 빗나갔습니다!" if lang == "Korean" else f"💨 {actor_name} attacks {target_name} but misses!"
                    print(cli_styles.gray(miss_msg))
            
            # --- ENEMY TURN ---
            elif actor_type == 'enemy':
                enemy_name = actor_name
                enemy_data = state['active_enemies'].get(enemy_name)
                if not enemy_data or enemy_data['hp'] <= 0:
                    continue
                    
                if enemy_data.get('surprised'):
                    print(cli_styles.yellow(f"\n⚡ {enemy_name} is surprised and skips their turn!"))
                    enemy_data['surprised'] = False
                    continue
                    
                if not conditions.can_act(enemy_data):
                    e_conds = conditions.get_active_conditions(enemy_data)
                    print(cli_styles.red(f"\n⚠️ {enemy_name} is incapacitated ({', '.join(e_conds)}) and cannot act!"))
                    continue
                
                target_stats = game_data['monsters'][enemy_data['type']]
                
                m_roll, m_hit_mod = random.randint(1, 20), 0
                m_atk_str = target_stats.get('attack', '+0 to hit, 1d4 damage')
                if hit_match := re.search(r'\+(\d+)', m_atk_str): m_hit_mod = int(hit_match.group(1))
                
                # 4.6 Target Selection (includes player and conscious companions)
                possible_targets = []
                if state['hp'] > 0:
                    possible_targets.append(state['name'])
                for comp in state.get('companions', []):
                    c_stats = state.get('companion_stats', {}).get(comp, {"hp": 0})
                    if c_stats['hp'] > 0:
                        possible_targets.append(comp)
                        
                if not possible_targets:
                    break
                    
                target = random.choice(possible_targets)
                is_ranged = 'bow' in m_atk_str.lower() or 'crossbow' in m_atk_str.lower()
                
                if target == state['name']:
                    # Advantage/disadvantage on enemy attack vs player
                    enemy_adv, enemy_dis = check_attack_advantage(enemy_data, state, is_ranged)
                    m_roll, m_detail = dice.roll_d20(advantage=enemy_adv, disadvantage=enemy_dis)
                    m_total = m_roll + m_hit_mod
                    
                    # 4.8 Apply player Cover AC bonus
                    player_ac = state.get('ac', 10) + state.get('cover_ac_bonus', 0)
                    cover_suffix = f" [Cover +{state['cover_ac_bonus']}]" if state.get('cover_ac_bonus') else ""
                    
                    print(f"\n🩸 {enemy_name} attacks YOU! Rolls {m_detail} + {m_hit_mod} = {m_total} vs AC {player_ac}{cover_suffix}")
                    if m_total >= player_ac:
                        m_dmg = dice.roll_from_string(m_atk_str.split(',')[-1], default_val=random.randint(1, 4))
                        
                        # Apply damage resistance if petrified
                        if conditions.has_effect(state, 'damage_resistance_all'):
                            m_dmg = m_dmg // 2
                            print(cli_styles.cyan(f"🛡️ Petrified Resistance halved damage!"))
                            
                        damage_player(state, m_dmg, is_crit=(m_roll == 20))
                        dmg_msg = f"으악! {enemy_name}의 공격이 명중했습니다! {m_dmg}의 피해를 입었습니다. (남은 HP: {state['hp']})" if lang == "Korean" else f"Ouch! {enemy_name} hits! You take {m_dmg} damage. (Remaining HP: {state['hp']})"
                        print(cli_styles.red(dmg_msg))
                    else: 
                        miss_msg = f"{enemy_name}의 공격이 당신을 빗나갔습니다!" if lang == "Korean" else f"{enemy_name} misses you!"
                        print(cli_styles.gray(miss_msg))
                else:
                    # Target is companion (check their specific AC)
                    c_stats = state['companion_stats'][target]
                    enemy_adv, enemy_dis = check_attack_advantage(enemy_data, {}, is_ranged)
                    m_roll, m_detail = dice.roll_d20(advantage=enemy_adv, disadvantage=enemy_dis)
                    m_total = m_roll + m_hit_mod
                    
                    print(f"\n🩸 {enemy_name} attacks companion {target}! Rolls {m_detail} + {m_hit_mod} = {m_total} vs AC {c_stats['ac']}")
                    if m_total >= c_stats['ac']:
                        m_dmg = dice.roll_from_string(m_atk_str.split(',')[-1], default_val=random.randint(1, 4))
                        c_stats['hp'] = max(0, c_stats['hp'] - m_dmg)
                        
                        dmg_comp = f"쿠쿵! {enemy_name}의 공격이 동료 {target}에게 명중했습니다! {m_dmg} 피해. (남은 HP: {c_stats['hp']}/{c_stats['max_hp']})" if lang == "Korean" else f"Ouch! {enemy_name} hits {target} for {m_dmg} damage! (HP: {c_stats['hp']}/{c_stats['max_hp']})"
                        print(cli_styles.red(dmg_comp))
                        if c_stats['hp'] <= 0:
                            print(cli_styles.red(f"💀 동료 {target}이(가) 쓰러졌습니다!"))
                    else:
                        miss_comp = f"{enemy_name}의 공격이 동료 {target}을(를) 빗나갔습니다!" if lang == "Korean" else f"{enemy_name} misses {target}!"
                        print(cli_styles.gray(miss_comp))
                        
        # End of round adjustments
        state['reaction_used'] = False
        for enemy_name, enemy_data in state['active_enemies'].items():
            enemy_data['reaction_used'] = False
            
        # Surprise flags reset after first round
        state.pop('companions_surprised', None)
        
        # 1.3 Tick down conditions at the end of the combat round
        expired = conditions.tick_conditions(state)
        for cond_name in expired:
            print(cli_styles.green(f"✦ Your {cond_name} condition has expired!"))
            
        for enemy_name, enemy_data in state['active_enemies'].items():
            if enemy_data['hp'] > 0:
                expired = conditions.tick_conditions(enemy_data)
                for cond_name in expired:
                    print(cli_styles.green(f"✦ {enemy_name}'s {cond_name} condition has expired!"))

    if state['hp'] <= 0:
        # Clean up combat state
        state.pop('active_enemies', None)
        state.pop('combat_initiative', None)
        state.pop('combat_surprise_processed', None)
        state.pop('player_surprised', None)
        state.pop('companions_surprised', None)
        state.pop('sneak_attack_used_this_turn', None)
        state.pop('concentrating_on', None)
        state.pop('cover_ac_bonus', None)
        return False, ""
        
    win_msg = "🎉 적들을 완벽히 토벌하고 전투에서 승리했습니다!" if lang == "Korean" else "🎉 You defeated the enemies!"
    print(cli_styles.green(f"\n{win_msg}"))
    
    # Calculate XP reward
    total_xp = 0
    if 'active_enemies' in state:
        for e_name, e_data in state['active_enemies'].items():
            e_type = e_data['type']
            if e_type in game_data.get("monsters", {}):
                total_xp += game_data["monsters"][e_type].get("xp", 0)
                
    if total_xp > 0:
        xp_msg = f"🏆 전투 승리로 {total_xp} XP를 획득했습니다!" if lang == "Korean" else f"🏆 You gained {total_xp} XP from the victory!"
        print(cli_styles.yellow(f"\n{xp_msg}"))
        import character
        character.check_level_up(state, total_xp)

    # Clean up combat state
    state.pop('active_enemies', None)
    state.pop('combat_initiative', None)
    state.pop('combat_surprise_processed', None)
    state.pop('player_surprised', None)
    state.pop('companions_surprised', None)
    state.pop('sneak_attack_used_this_turn', None)
    state.pop('cover_ac_bonus', None)
    
    action_log = "I fought and killed the enemies."
    if lang == "Korean":
        action_log = "내가 앞선 전투에서 모든 적들을 무찌르고 승리했다."
    return True, action_log