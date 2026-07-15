import random
import dice
import cli_styles
import skills_data
import class_features

def get_proper_stats(c_class):
    c = c_class.lower()
    if any(x in c for x in ['fighter', 'barbarian', 'paladin']): return {"STR": 15, "DEX": 13, "CON": 14, "INT": 8, "WIS": 12, "CHA": 10}
    elif any(x in c for x in ['wizard', 'sorcerer', 'artificer']): return {"STR": 8, "DEX": 14, "CON": 13, "INT": 15, "WIS": 12, "CHA": 10}
    elif any(x in c for x in ['rogue', 'ranger', 'monk']): return {"STR": 8, "DEX": 15, "CON": 13, "INT": 14, "WIS": 10, "CHA": 12}
    elif any(x in c for x in ['cleric', 'druid']): return {"STR": 13, "DEX": 8, "CON": 14, "INT": 10, "WIS": 15, "CHA": 12}
    elif any(x in c for x in ['bard', 'warlock']): return {"STR": 8, "DEX": 13, "CON": 12, "INT": 10, "WIS": 14, "CHA": 15}
    return {"STR": 12, "DEX": 12, "CON": 12, "INT": 12, "WIS": 12, "CHA": 12}

def create_character():
    cli_styles.draw_box("CHARACTER CREATION / 캐릭터 생성", [
        "Welcome! Let's create your D&D character.",
        "새로운 모험을 떠날 캐릭터를 만들어 봅시다!"
    ], cli_styles.PURPLE)
    
    # 0. Language Selection
    print("\n--- Choose Language / 언어 선택 ---")
    print("1. English")
    print("2. 한국어 (Korean)")
    lang_choice = input("Select (1/2, default 2): ").strip()
    language = "English" if lang_choice == '1' else "Korean"
    
    if language == "Korean":
        name = input("\n캐릭터의 이름을 입력하세요: ").strip() or "영웅"
        
        print("\n--- 종족 선택 (Choose Heritage) ---")
        print("- Human (인간): 다재다능하고 다양한 분야에 적응력이 뛰어납니다. (모든 능력치 +1)")
        print("- Elf (엘프): 우아하며 장수하며 마법과 자연에 친화적입니다. (DEX +2, 민감함 숙련)")
        print("- Dwarf (드워프): 튼튼하고 뚝심 있으며 독극물 저항이 강합니다. (CON +2)")
        print("- Orc (오크): 강력한 신체 능력을 가진 전사입니다. (STR +2, CON +1, 위협 숙련)")
        print("- Halfling (하프링): 작고 재빠르며, 운이 좋고 은밀합니다. (DEX +2)")
        race = input("종족을 선택하세요 (Human, Elf, Dwarf, Orc, Halfling): ").strip().title() or "Human"
        
        print("\n--- 직업 선택 (Choose Path) ---")
        print("- Fighter (전사): 무기 전투의 대가. (시작 스킬: Second Wind, HD: d10)")
        print("- Rogue (도적): 민첩하고 치명적인 공격. (시작 스킬: Sneak Attack, HD: d8)")
        print("- Wizard (마법사): 강력한 원소 마법 구사. (시작 마법: Magic Missile, Shield, HD: d6)")
        print("- Cleric (성직자): 신성한 마법과 치유의 전사. (시작 마법: Healing Word, Sacred Flame, HD: d8)")
        print("- Bard (바드): 시와 음악의 예술가. (시작 마법: Healing Word, HD: d8)")
        char_class = input("직업을 선택하세요 (Fighter, Rogue, Wizard, Cleric, Bard): ").strip().title() or "Fighter"
        
        print("\n--- 캐릭터의 스토리 배경 ---")
        background = input("캐릭터의 출신 배경 (예: Soldier, Criminal, Noble, Acolyte): ").strip() or "Soldier"
        appearance = input("외형 묘사: ").strip() or "평범한 모험가"
        backstory = input("짧은 과거 배경 이야기: ").strip() or "새로운 모험을 찾아 떠난 모험가"
    else:
        name = input("\nEnter your character's name: ").strip() or "Hero"
        
        print("\n--- Choose Your Heritage ---")
        print("- Human: All stats +1.")
        print("- Elf: DEX +2, Perception skill.")
        print("- Dwarf: CON +2.")
        print("- Orc: STR +2, CON +1, Intimidation skill.")
        print("- Halfling: DEX +2.")
        race = input("Choose your race (Human, Elf, Dwarf, Orc, Halfling): ").strip().title() or "Human"
        
        print("\n--- Choose Your Path ---")
        print("- Fighter: Martial weapon master. (HD: d10)")
        print("- Rogue: Dextrous stealth attacker. (HD: d8)")
        print("- Wizard: Scholarly spellcaster. (HD: d6)")
        print("- Cleric: Divine warrior and healer. (HD: d8)")
        print("- Bard: Magical musician. (HD: d8)")
        char_class = input("Choose your class (Fighter, Rogue, Wizard, Cleric, Bard): ").strip().title() or "Fighter"
        
        print("\n--- Narrative Details ---")
        background = input("Character background (e.g. Soldier, Noble): ").strip() or "Soldier"
        appearance = input("Describe appearance: ").strip() or "Ordinary adventurer"
        backstory = input("Brief backstory: ").strip() or "Seeking glory and adventure"

    # Normalize inputs
    if race not in skills_data.RACE_DATA:
        race = "Human"
    if char_class not in skills_data.CLASS_SKILL_OPTIONS:
        char_class = "Fighter"

    # Stat Roller
    print("\nAbility Score Generation / 능력치 판정 방식:")
    print("1. Manual  (직접 입력)")
    print("2. Proper  (직업별 최적화 능력치)")
    print("3. Chaotic (완전 랜덤 3-18)")
    print("4. Natural (최적화 베이스에 약간의 주사위 변동)")
    stat_choice = input("Select (1/2/3/4, default 2): ").strip()
    
    if stat_choice == '1':
        print("\nEnter Ability Scores (8-20). Default is 10.")
        def get_stat(stat_name):
            while True:
                val = input(f"{stat_name}: ").strip()
                if not val:
                    return 10
                try:
                    num = int(val)
                    if num < 8 or num > 20:
                        if language == "Korean":
                            confirm = input(f"⚠️ 경고: 입력한 수치({num})가 권장 범위(8-20)를 벗어납니다. 정말 이 스탯으로 진행하시겠습니까? (y/n, 기본 y): ").strip().lower()
                        else:
                            confirm = input(f"⚠️ Warning: Score ({num}) is outside the recommended range (8-20). Do you really want to proceed with this stat? (y/n, default y): ").strip().lower()
                        if confirm == 'n':
                            continue
                    return num
                except ValueError:
                    if language == "Korean":
                        print("❌ 오류: 올바른 정수를 입력해 주세요.")
                    else:
                        print("❌ Error: Please enter a valid integer.")
        stats = {
            "STR": get_stat("Strength (근력)"),
            "DEX": get_stat("Dexterity (민첩)"),
            "CON": get_stat("Constitution (체력)"),
            "INT": get_stat("Intelligence (지능)"),
            "WIS": get_stat("Wisdom (지혜)"),
            "CHA": get_stat("Charisma (매력)")
        }
    elif stat_choice == '3':
        stats = {s: random.randint(3, 18) for s in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
    elif stat_choice == '4':
        base = get_proper_stats(char_class)
        stats = {s: max(3, min(20, val + random.randint(-2, 2))) for s, val in base.items()}
    else:
        stats = get_proper_stats(char_class)

    # 2.5 Apply Racial Stat Bonuses
    r_info = skills_data.RACE_DATA[race]
    for stat_name, bonus in r_info['stat_bonuses'].items():
        stats[stat_name] = min(20, stats.get(stat_name, 10) + bonus)
    
    racial_traits = list(r_info['traits'])
    speed = r_info['speed']
    languages = list(r_info['languages'])

    # Class-specific Starting Equipment, Spells
    c_lower = char_class.lower()
    spells = []
    
    if 'fighter' in c_lower:
        weapon = "Greatsword"
        armor = "Chain Mail"
        spells = ["Second Wind"]
    elif 'rogue' in c_lower:
        weapon = "Dagger"
        armor = "Leather Armor"
        spells = ["Sneak Attack"]
    elif 'wizard' in c_lower:
        weapon = "Dagger"
        armor = "None"
        spells = ["Magic Missile", "Shield (Spell)"]
    elif 'cleric' in c_lower:
        weapon = "Mace"
        armor = "Scale Mail"
        spells = ["Healing Word", "Sacred Flame"]
    elif 'bard' in c_lower:
        weapon = "Shortsword"
        armor = "Leather Armor"
        spells = ["Healing Word"]
    else:
        weapon = "Dagger"
        armor = "None"

    # 2.1 Skill Proficiencies Selection
    skill_proficiencies = []
    
    # Add racial skill bonuses
    r_skills = skills_data.RACE_SKILL_BONUSES.get(race, [])
    for rs in r_skills:
        if rs not in skill_proficiencies:
            skill_proficiencies.append(rs)
            
    # Class skill choices
    class_opt = skills_data.CLASS_SKILL_OPTIONS[char_class]
    opt_count = class_opt['count']
    choices = [c for c in class_opt['choices'] if c not in skill_proficiencies]
    
    if choices:
        prompt_sk = f"\n선택 가능한 스킬 목록에서 {opt_count}개를 고르세요:" if language == "Korean" else f"\nChoose {opt_count} skills from the list:"
        print(prompt_sk)
        for i, sk in enumerate(choices, 1):
            print(f"{i}. {sk} ({skills_data.SKILLS[sk]})")
            
        chosen_indices = []
        while len(chosen_indices) < opt_count:
            try:
                msg_sel = f"선택 [{len(chosen_indices)+1}/{opt_count}] > " if language == "Korean" else f"Choose [{len(chosen_indices)+1}/{opt_count}] > "
                sel = int(input(msg_sel)) - 1
                if 0 <= sel < len(choices) and sel not in chosen_indices:
                    chosen_indices.append(sel)
                else:
                    print("Invalid choice or already selected.")
            except ValueError:
                print("Please enter a valid number.")
        for idx in chosen_indices:
            skill_proficiencies.append(choices[idx])

    # Expertise selection for Rogue
    expertise = []
    if char_class == 'Rogue':
        prompt_exp = "\n전문화(Expertise)할 스킬 2개를 선택하세요 (보너스 2배 적용):" if language == "Korean" else "\nSelect 2 skills for Expertise (Double proficiency bonus):"
        print(prompt_exp)
        for i, sk in enumerate(skill_proficiencies, 1):
            print(f"{i}. {sk}")
        exp_indices = []
        while len(exp_indices) < 2:
            try:
                msg_sel = f"선택 [{len(exp_indices)+1}/2] > " if language == "Korean" else f"Choose [{len(exp_indices)+1}/2] > "
                sel = int(input(msg_sel)) - 1
                if 0 <= sel < len(skill_proficiencies) and sel not in exp_indices:
                    exp_indices.append(sel)
                else:
                    print("Invalid choice or already selected.")
            except ValueError:
                print("Please enter a valid number.")
        for idx in exp_indices:
            expertise.append(skill_proficiencies[idx])

    # 2.2 Saving Throw Proficiencies
    save_proficiencies = skills_data.CLASS_SAVE_PROFICIENCIES.get(char_class, ['DEX', 'CON'])

    # 2.3 Class Hit Dice & HP calculation
    hit_die = skills_data.CLASS_HIT_DICE.get(char_class, 8)
    con_mod = dice.get_modifier(stats["CON"])
    max_hp = max(1, hit_die + con_mod)

    # Base MP
    if any(x in c_lower for x in ['wizard', 'sorcerer', 'warlock']):
        max_mp = 10 + dice.get_modifier(stats["INT"] if 'wizard' in c_lower else stats["CHA"])
    elif any(x in c_lower for x in ['cleric', 'druid', 'bard']):
        max_mp = 10 + dice.get_modifier(stats["WIS"] if 'cleric' in c_lower or 'druid' in c_lower else stats["CHA"])
    elif any(x in c_lower for x in ['paladin', 'ranger']):
        max_mp = 5
    else:
        max_mp = 0

    # Setup Inventory
    inventory = [weapon, "Health Potion", "Mana Potion"]
    if armor != "None":
        inventory.append(armor)

    state = {
        "name": name, "race": race, "class": char_class,
        "background": background, "appearance": appearance, "backstory": backstory,
        "ac": 10,
        "equipped_weapon": weapon, "equipped_armor": armor, "equipped_shield": "None",
        "hp": max_hp, "max_hp": max_hp, "level": 1, "xp": 0, "gold": 50,
        "mp": max_mp, "max_mp": max_mp, "spells": spells,
        "stats": stats, "inventory": inventory,
        "location": "The Town", "history": [], "companions": [], "language": language,
        
        # Phase 2 additions
        "hit_die": hit_die,
        "hit_dice_remaining": 1,
        "skill_proficiencies": skill_proficiencies,
        "expertise": expertise,
        "save_proficiencies": save_proficiencies,
        "racial_traits": racial_traits,
        "speed": speed,
        "languages": languages,
        "passive_perception": 10 + dice.get_modifier(stats["WIS"]) + (2 if "Perception" in skill_proficiencies else 0),
        "class_features": {},
        # Phase 3 additions
        "spell_slots_max": skills_data.get_slots_for_class_and_level(char_class, 1),
        "spell_slots": dict(skills_data.get_slots_for_class_and_level(char_class, 1)),
        "use_spell_slots": True,
        "concentrating_on": None,
    }
    
    # Initialize Level 1 class features
    lvl1_feats = class_features.get_features_at_level(char_class, 1)
    for feat in lvl1_feats:
        state["class_features"][feat["name"]] = {"uses_remaining": feat.get("max_uses", 1), "max_uses": feat.get("max_uses", 1)}
    
    from game_state import load_game_data
    import actions
    actions.recalculate_ac(state, load_game_data())
    
    welcome_msg = f"Welcome, {name} the {race} {char_class}! Your adventure begins."
    if language == "Korean":
        welcome_msg = f"환영합니다, {race} {char_class}인 {name}! 당신의 위대한 모험이 지금 시작됩니다."
        
    cli_styles.draw_box("CREATED", [welcome_msg], cli_styles.GREEN)
    return state

def _get_mp_stat(char_class):
    c_lower = char_class.lower()
    if 'wizard' in c_lower:
        return 'INT'
    elif any(x in c_lower for x in ['sorcerer', 'warlock', 'bard']):
        return 'CHA'
    elif any(x in c_lower for x in ['cleric', 'druid']):
        return 'WIS'
    return None

def handle_asi(state):
    lang = state.get('language', 'Korean')
    stats = ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']
    
    if lang == "Korean":
        print("\n🏆 능력치 상승(ASI) 획득! 다음 중 선택하세요:")
        print("1. 하나의 능력치 +2")
        print("2. 서로 다른 두 개의 능력치 각각 +1")
        choice = input("선택 (1/2, 기본 1): ").strip()
        
        if choice == '2':
            # Two stats +1
            for i in range(2):
                while True:
                    stat_up = input(f"[{i+1}/2] 올릴 능력치 명칭 입력 (STR, DEX, CON, INT, WIS, CHA): ").upper()
                    if stat_up in stats:
                        state['stats'][stat_up] = min(20, state['stats'][stat_up] + 1)
                        print(f"{stat_up} 능력치가 이제 {state['stats'][stat_up]}이(가) 되었습니다!")
                        break
                    print("잘못된 명칭입니다.")
        else:
            # One stat +2
            while True:
                stat_up = input("올릴 능력치 명칭 입력 (STR, DEX, CON, INT, WIS, CHA): ").upper()
                if stat_up in stats:
                    state['stats'][stat_up] = min(20, state['stats'][stat_up] + 2)
                    print(f"{stat_up} 능력치가 이제 {state['stats'][stat_up]}이(가) 되었습니다!")
                    break
                print("잘못된 명칭입니다.")
    else:
        print("\n🏆 Ability Score Improvement (ASI) gained! Choose option:")
        print("1. Increase one score by 2")
        print("2. Increase two different scores by 1 each")
        choice = input("Select (1/2, default 1): ").strip()
        
        if choice == '2':
            for i in range(2):
                while True:
                    stat_up = input(f"[{i+1}/2] Choose stat (STR, DEX, CON, INT, WIS, CHA): ").upper()
                    if stat_up in stats:
                        state['stats'][stat_up] = min(20, state['stats'][stat_up] + 1)
                        print(f"Your {stat_up} is now {state['stats'][stat_up]}!")
                        break
                    print("Invalid stat name.")
        else:
            while True:
                stat_up = input("Choose stat (STR, DEX, CON, INT, WIS, CHA): ").upper()
                if stat_up in stats:
                    state['stats'][stat_up] = min(20, state['stats'][stat_up] + 2)
                    print(f"Your {stat_up} is now {state['stats'][stat_up]}!")
                    break
                print("Invalid stat name.")

def check_level_up(state, gained_xp):
    state['xp'] = state.get('xp', 0) + gained_xp
    leveled_up = False
    
    while state['level'] < 20:
        next_level = state['level'] + 1
        threshold = skills_data.XP_THRESHOLDS.get(next_level, 999999)
        
        if state['xp'] >= threshold:
            state['level'] = next_level
            leveled_up = True
            
            # 2.3 Class hit dice HP scaling (avg + CON mod)
            hit_die = state.get('hit_die', 8)
            avg_roll = hit_die // 2 + 1
            con_mod = dice.get_modifier(state['stats']['CON'])
            hp_increase = max(1, avg_roll + con_mod)
            state['max_hp'] += hp_increase
            state['hp'] = state['max_hp']
            
            state['hit_dice_remaining'] = state['level']
            
            # MP Increase
            if state.get('max_mp', 0) > 0:
                mp_stat = _get_mp_stat(state['class'])
                mp_mod = dice.get_modifier(state['stats'][mp_stat]) if mp_stat else 0
                mp_increase = max(1, 2 + mp_mod)
                state['max_mp'] += mp_increase
                state['mp'] = state['max_mp']
                
            # Phase 3 Spell slots recalculation
            max_slots = skills_data.get_slots_for_class_and_level(state['class'], state['level'])
            state['spell_slots_max'] = max_slots
            state['spell_slots'] = dict(max_slots)
                
            # Class features unlocked
            new_feats = class_features.get_features_at_level(state['class'], state['level'])
            for feat in new_feats:
                if feat["name"] not in state["class_features"]:
                    state["class_features"][feat["name"]] = {"uses_remaining": feat.get("max_uses", 1), "max_uses": feat.get("max_uses", 1)}
                if feat["name"] not in state.get('spells', []):
                    if 'spells' not in state:
                        state['spells'] = []
                    state['spells'].append(feat["name"])
            
            lang = state.get('language', 'Korean')
            if lang == "Korean":
                msg = f"🎉 레벨 업! 이제 레벨 {state['level']}이 되었습니다! 🎉\n최대 HP가 {hp_increase} 증가했습니다."
                cli_styles.draw_box("레벨 업", [msg], cli_styles.YELLOW)
            else:
                msg = f"🎉 LEVEL UP! You are now Level {state['level']}! 🎉\nMax HP increased by {hp_increase}."
                cli_styles.draw_box("LEVEL UP", [msg], cli_styles.YELLOW)
                
            # 2.4 ASI at levels 4, 8, 12, 16, 19
            if state['level'] in [4, 8, 12, 16, 19]:
                handle_asi(state)
                
            # Update passive perception
            state['passive_perception'] = 10 + dice.get_modifier(state['stats']["WIS"]) + (2 + ((state['level'] - 1) // 4) if "Perception" in state.get('skill_proficiencies', []) else 0)
        else:
            break
            
    if not leveled_up and gained_xp > 0:
        next_lvl = state['level'] + 1
        threshold = skills_data.XP_THRESHOLDS.get(next_lvl, '???')
        print(f"  +{gained_xp} XP ({state['xp']}/{threshold})")