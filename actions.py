import re
import random
import dice
import cli_styles
import skills_data

def get_armor_category(item_name, item_info):
    if not item_info:
        return 'light'
    armor_type = item_info.get('armor_type')
    if armor_type:
        return armor_type.lower()
        
    name_l = item_name.lower()
    desc_l = item_info.get('description', '').lower()
    
    if 'shield' in name_l:
        return 'shield'
    if any(x in name_l or x in desc_l for x in ['plate', 'splint', 'ring mail', 'chain mail']):
        return 'heavy'
    if any(x in name_l or x in desc_l for x in ['hide', 'chain shirt', 'scale mail', 'breastplate', 'half plate']):
        return 'medium'
    return 'light'

def recalculate_ac(state, game_data):
    # Base AC is 10 + DEX mod
    dex_mod = dice.get_modifier(state['stats'].get('DEX', 10))
    ac = 10 + dex_mod
    
    eq_armor = state.get('equipped_armor')
    eq_shield = state.get('equipped_shield')
    
    # Process Body Armor
    if eq_armor and eq_armor != 'None':
        armor_info = game_data.get('items', {}).get(eq_armor)
        if armor_info:
            desc = armor_info.get('description', '')
            # Parse 'AC 11 + DEX' or 'AC 16'
            match = re.search(r'AC\s+(\d+)', desc, re.IGNORECASE)
            if match:
                base_ac = int(match.group(1))
                category = get_armor_category(eq_armor, armor_info)
                if category == 'light':
                    ac = base_ac + dex_mod
                elif category == 'medium':
                    ac = base_ac + min(dex_mod, 2)
                else: # heavy
                    ac = base_ac
                    
    # Process Shield
    if eq_shield and eq_shield != 'None':
        shield_info = game_data.get('items', {}).get(eq_shield)
        if shield_info:
            desc = shield_info.get('description', '')
            match = re.search(r'AC\s+\+(\d+)', desc, re.IGNORECASE)
            if match:
                ac += int(match.group(1))
            elif '+2' in desc or '+ 2' in desc:
                ac += 2
                
    state['ac'] = ac

def show_status(state):
    lang = state.get('language', 'Korean')
    title = f"🛡️ {state['name']} - Character Sheet / 캐릭터 정보 🛡️"
    
    lines = [
        f"Name: {cli_styles.bold(state['name'])} | Level: {state['level']} | Class: {state['class']} | Race: {state['race']}",
        f"XP: {state.get('xp', 0)} | Gold: {state.get('gold', 50)} GP",
        f"Location: {state.get('location', 'The Town')}",
        f"--------------------------------------------------",
        f"HP: {state['hp']}/{state['max_hp']} | MP: {state['mp']}/{state['max_mp'] if state['max_mp'] > 0 else 'N/A'}",
        f"AC: {state.get('ac', 10)} | Speed: {state.get('speed', 30)} ft | Passive Perception: {state.get('passive_perception', 10)}",
        f"----------------- Ability Scores -----------------"
    ]
    
    for s_name, score in state['stats'].items():
        modifier = dice.get_modifier(score)
        mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
        lines.append(f"  {s_name:<4}: {score:>2} ({mod_str})")
        
    lines.append(f"------------------- Equipment -------------------")
    lines.append(f"  Weapon: {state.get('equipped_weapon', 'None')}")
    lines.append(f"  Armor : {state.get('equipped_armor', 'None')}")
    lines.append(f"  Shield: {state.get('equipped_shield', 'None')}")
    
    # Phase 2 Details in Status
    lines.append(f"------------------- Proficiencies ----------------")
    lines.append(f"  Skill Profs: {', '.join(state.get('skill_proficiencies', []))}")
    if state.get('expertise'):
        lines.append(f"  Expertise  : {', '.join(state.get('expertise', []))}")
    lines.append(f"  Saves Profs: {', '.join(state.get('save_proficiencies', []))}")
    lines.append(f"  Languages  : {', '.join(state.get('languages', ['Common']))}")
    
    if state.get('racial_traits'):
        lines.append(f"  Traits     : {', '.join(state.get('racial_traits', []))}")
        
    if state.get('inventory'):
        lines.append(f"------------------- Inventory -------------------")
        lines.append(f"  {', '.join(state['inventory'])}")
        
    if state.get('spells'):
        lines.append(f"--------------------- Spells --------------------")
        lines.append(f"  {', '.join(state['spells'])}")
        
    cli_styles.draw_box(title, lines, cli_styles.PURPLE)

def handle_shop(state, game_data):
    lang = state.get('language', 'Korean')
    
    title = "상점 거래" if lang == "Korean" else "MERCHANT SHOP"
    lines = [f"Gold: {state.get('gold', 50)} GP", "Available Items for Sale:"]
    
    shop_items = game_data.get("items", {})
    item_list = list(shop_items.keys())
    for i, item_name in enumerate(item_list, 1):
        price = shop_items[item_name].get("price", 0)
        desc = shop_items[item_name].get("description", "")
        lines.append(f"{i}. {item_name:<15} - {price:>3} GP | {desc}")
        
    cli_styles.draw_box(title, lines, cli_styles.YELLOW)
    
    prompt = "구매할 아이템의 이름을 입력하세요 (취소하려면 엔터): " if lang == "Korean" else "Enter the name of the item to buy (or press Enter to cancel): "
    buy_choice = input(prompt).strip().title()
    
    if buy_choice in shop_items:
        price = shop_items[buy_choice].get("price", 0)
        if state.get("gold", 0) >= price:
            state["gold"] = state.get("gold", 0) - price
            state["inventory"].append(buy_choice)
            
            success_msg = f"[성공] {buy_choice}을(를) {price} GP에 구매했습니다!" if lang == "Korean" else f"[Success] You bought a {buy_choice} for {price} GP!"
            print(cli_styles.green(f"\n{success_msg}"))
            return True
        else:
            fail_gold = "[실패] 골드가 부족합니다!" if lang == "Korean" else "[Failed] Not enough gold!"
            print(cli_styles.red(f"\n{fail_gold}"))
    elif buy_choice:
        fail_item = "[실패] 상점에 존재하지 않는 아이템입니다." if lang == "Korean" else "[Failed] Item not found in shop database."
        print(cli_styles.red(f"\n{fail_item}"))
    return False

def handle_equip(state, game_data):
    lang = state.get('language', 'Korean')
    
    title = "장착 관리" if lang == "Korean" else "EQUIPMENT MANAGEMENT"
    lines = [f"Inventory: {', '.join(state['inventory'])}"]
    cli_styles.draw_box(title, lines, cli_styles.CYAN)
    
    prompt = "장착할 아이템 이름을 입력하세요 (취소하려면 엔터): " if lang == "Korean" else "Enter the name of the item to equip (or press Enter to cancel): "
    item_to_equip = input(prompt).strip().title()
    
    if item_to_equip in state['inventory']:
        item_info = game_data.get('items', {}).get(item_to_equip)
        if not item_info:
            print(cli_styles.red("\n[Error] Invalid item details in game database."))
            return False
            
        item_type = item_info.get("type", "weapon")
        
        if item_type == "weapon": 
            state['equipped_weapon'] = item_to_equip
            msg = f"{item_to_equip}을(를) 무기로 장착했습니다." if lang == "Korean" else f"Equipped {item_to_equip} as your weapon."
            print(cli_styles.green(f"\n[Success] {msg}"))
            return True
        elif item_type == "armor": 
            # 4.2 Armor proficiency checks
            category = get_armor_category(item_to_equip, item_info)
                
            profs = skills_data.CLASS_ARMOR_PROFICIENCY.get(state['class'], [])
            if category not in profs:
                state['armor_penalty'] = True
                warn = "⚠ WARNING: You are not proficient with this armor! You will have disadvantage on STR/DEX rolls and cannot cast spells!" if lang != "Korean" else "⚠ 경고: 이 방어구에 숙련되어 있지 않습니다! 힘/민첩 판정에 불이익(Disadvantage)이 주어지며 마법을 시전할 수 없습니다!"
                print(cli_styles.yellow(f"\n{warn}"))
            else:
                state['armor_penalty'] = False
                
            # Reset speed to race base speed, then apply heavy armor penalty if needed
            base_speed = skills_data.RACE_DATA.get(state['race'], {}).get('speed', 30)
            state['speed'] = base_speed
            if category == 'heavy' and state['stats']['STR'] < 13:
                warn_str = "⚠ STR is too low for this heavy armor! Speed reduced by 10 feet." if lang != "Korean" else "⚠ 근력이 부족하여 이동속도가 10피트 감소합니다!"
                print(cli_styles.yellow(f"\n{warn_str}"))
                state['speed'] = max(10, base_speed - 10)
                
            # Separate logic for shield vs body armor
            if "shield" in item_to_equip.lower():
                state['equipped_shield'] = item_to_equip
                recalculate_ac(state, game_data)
                msg = f"{item_to_equip}을(를) 방패로 장착했습니다. (새로운 AC: {state['ac']})" if lang == "Korean" else f"Equipped {item_to_equip} as your shield. (New AC: {state['ac']})"
            else:
                state['equipped_armor'] = item_to_equip
                recalculate_ac(state, game_data)
                msg = f"{item_to_equip}을(를) 방어구로 장착했습니다. (새로운 AC: {state['ac']})" if lang == "Korean" else f"Equipped {item_to_equip} as your armor. (New AC: {state['ac']})"
            
            print(cli_styles.green(f"\n[Success] {msg}"))
            return True
        else:
            msg = "소모성 아이템은 장착할 수 없습니다. 'use' 명령어를 사용하세요." if lang == "Korean" else "Consumable items cannot be equipped. Use 'use' command instead."
            print(cli_styles.red(f"\n[Failed] {msg}"))
    elif item_to_equip:
        msg = "인벤토리에 해당 아이템이 존재하지 않습니다." if lang == "Korean" else "You don't have that item in your inventory."
        print(cli_styles.red(f"\n[Failed] {msg}"))
    return False

def handle_use(state, game_data):
    lang = state.get('language', 'Korean')
    
    title = "아이템 사용" if lang == "Korean" else "USE ITEM"
    consumables = [item for item in state['inventory'] if game_data.get('items', {}).get(item, {}).get('type') == 'consumable']
    
    if not consumables:
        msg = "인벤토리에 소모성 아이템이 없습니다." if lang == "Korean" else "No consumable items in your inventory."
        print(cli_styles.red(f"\n{msg}"))
        return False
        
    lines = [f"Consumables: {', '.join(consumables)}"]
    cli_styles.draw_box(title, lines, cli_styles.CYAN)
    
    prompt = "사용할 아이템 이름을 입력하세요 (취소하려면 엔터): " if lang == "Korean" else "Enter item name to use (or press Enter to cancel): "
    item_to_use = input(prompt).strip().title()
    
    if item_to_use in state['inventory']:
        item_info = game_data['items'][item_to_use]
        if item_info.get('type') == 'consumable':
            desc = item_info.get('description', '')
            roll_val = dice.roll_from_string(desc)
            
            # Apply potion healing/recovery
            if 'heal' in desc.lower() or 'hp' in desc.lower():
                old_hp = state['hp']
                state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + roll_val)
                state['inventory'].remove(item_to_use)
                
                msg = f"{item_to_use}을(를) 사용하여 {state['hp'] - old_hp} HP를 회복했습니다!" if lang == "Korean" else f"Used {item_to_use} and recovered {state['hp'] - old_hp} HP!"
                print(cli_styles.green(f"\n[Success] {msg} (HP: {state['hp']}/{state['max_hp']})"))
                return True
            elif 'mp' in desc.lower() or 'restore' in desc.lower():
                if state.get('max_mp', 0) > 0:
                    old_mp = state['mp']
                    state['mp'] = min(state['max_mp'], state['mp'] + roll_val)
                    state['inventory'].remove(item_to_use)
                    
                    msg = f"{item_to_use}을(를) 사용하여 {state['mp'] - old_mp} MP를 복구했습니다!" if lang == "Korean" else f"Used {item_to_use} and restored {state['mp'] - old_mp} MP!"
                    print(cli_styles.green(f"\n[Success] {msg} (MP: {state['mp']}/{state['max_mp']})"))
                    return True
                else:
                    msg = "당신은 마나 풀이 활성화되어 있지 않습니다!" if lang == "Korean" else "You do not have a mana pool!"
                    print(cli_styles.red(f"\n[Failed] {msg}"))
        else:
            msg = "소모성 아이템만 사용할 수 있습니다." if lang == "Korean" else "Only consumable items can be used here."
            print(cli_styles.red(f"\n[Failed] {msg}"))
    elif item_to_use:
        msg = "인벤토리에 해당 아이템이 존재하지 않습니다." if lang == "Korean" else "You don't have that item in your inventory."
        print(cli_styles.red(f"\n[Failed] {msg}"))
    return False

def handle_rest(state):
    lang = state.get('language', 'Korean')
    
    title = "휴식 및 정비" if lang == "Korean" else "CAMP & REST"
    if lang == "Korean":
        lines = [
            "1. Short Rest (단기 휴식 - 히트 다이스를 소비하여 체력 회복, 어디서나 가능)",
            "2. Long Rest  (장기 휴식 - 체력 및 마나 완전 회복, 안전지대 필요)"
        ]
        prompt = "휴식 유형을 선택하세요 (1/2, 취소하려면 엔터): "
    else:
        lines = [
            "1. Short Rest (Spend hit dice to heal, can be done anywhere)",
            "2. Long Rest  (Fully recover all HP/MP/slots, requires a safe location)"
        ]
        prompt = "Choose a rest type (1/2, or press Enter to cancel): "
        
    cli_styles.draw_box(title, lines, cli_styles.BLUE)
    choice = input(prompt).strip()
    
    if choice == '1':
        # 4.4 Short Rest spending hit dice
        hit_die = state.get('hit_die', 8)
        remaining = state.get('hit_dice_remaining', 0)
        
        if remaining <= 0:
            msg = "남은 히트 다이스가 없습니다! 체력을 수동으로 회복할 수 없습니다." if lang == "Korean" else "No hit dice remaining! You cannot heal during this short rest."
            print(cli_styles.red(f"\n[Failed] {msg}"))
            return False
            
        con_mod = dice.get_modifier(state['stats']['CON'])
        healed_total = 0
        
        print(f"\n--- Short Rest (Hit Dice: {remaining}d{hit_die} remaining) ---")
        while remaining > 0 and state['hp'] < state['max_hp']:
            prompt_hd = f"히트 다이스(d{hit_die})를 사용하여 치유하시겠습니까? (남은 개수: {remaining}) [y/n]: " if lang == "Korean" else f"Spend a hit die (1d{hit_die} + {con_mod}) to heal? (Remaining: {remaining}) [y/n]: "
            sd_choice = input(prompt_hd).strip().lower()
            if sd_choice != 'y':
                break
                
            roll = random.randint(1, hit_die)
            heal = max(1, roll + con_mod)
            old_hp = state['hp']
            state['hp'] = min(state['max_hp'], state['hp'] + heal)
            healed = state['hp'] - old_hp
            healed_total += healed
            remaining -= 1
            
            print(f"🎲 Rolled: {roll} + CON {con_mod} = {heal} (Healed: {healed} HP). Current HP: {state['hp']}/{state['max_hp']}")
            
        state['hit_dice_remaining'] = remaining
        
        # Recover MP/spell slots: MP recovers 50% max
        if not state.get('use_spell_slots') and state.get('max_mp', 0) > 0:
            state['mp'] = min(state['max_mp'], state.get('mp', 0) + (state['max_mp'] // 2))
            
        msg = f"단기 휴식 완료! 총 {healed_total} HP 회복. (체력: {state['hp']}/{state['max_hp']})" if lang == "Korean" else f"Short rest complete! Total healed: {healed_total} HP. (HP: {state['hp']}/{state['max_hp']})"
        print(cli_styles.green(f"\n[Success] {msg}"))
        return True
    elif choice == '2':
        if state.get('is_safe', False) or state.get('can_shop', False):
            state['hp'] = state.get('max_hp', state['hp'])
            if state.get('max_mp', 0) > 0: state['mp'] = state['max_mp']
            
            # Phase 3 Spell slots recovery on long rest
            if state.get('use_spell_slots'):
                state['spell_slots'] = dict(state.get('spell_slots_max', {}))
                
            # 4.4 Recover up to half of hit dice
            recovered_hd = max(1, state['level'] // 2)
            state['hit_dice_remaining'] = min(state['level'], state.get('hit_dice_remaining', 0) + recovered_hd)
            
            # Recover companion HP
            for companion_name in state.get('companions', []):
                if companion_name in state.get('companion_stats', {}):
                    state['companion_stats'][companion_name]['hp'] = state['companion_stats'][companion_name]['max_hp']
            
            msg = "안전하고 아늑한 곳에서 긴 휴식을 취했습니다. 완전히 피로를 회복했습니다!" if lang == "Korean" else "You took a long rest in a safe place. You are fully recovered!"
            print(cli_styles.green(f"\n[Success] {msg}"))
            return True
        else:
            msg = "이곳은 장기 휴식을 취하기에 너무 위험합니다! 안전한 마을이나 초소를 찾으세요." if lang == "Korean" else "It's too dangerous to take a Long Rest here! Find a town, inn, or secure camp."
            print(cli_styles.red(f"\n[Failed] {msg}"))
    return False

def handle_sell(state, game_data):
    lang = state.get('language', 'Korean')
    
    if not state.get('inventory'):
        msg = "인벤토리가 비어 있습니다." if lang == "Korean" else "Your inventory is empty."
        print(cli_styles.red(f"\n{msg}"))
        return False
        
    title = "아이템 판매" if lang == "Korean" else "SELL ITEMS"
    
    # Render inventory with half-price values
    sellable_items = []
    for item in state['inventory']:
        # Don't sell currently equipped items
        if item in [state.get('equipped_weapon'), state.get('equipped_armor'), state.get('equipped_shield')]:
            continue
        item_info = game_data.get('items', {}).get(item)
        if item_info:
            price = item_info.get('price', 0) // 2
            sellable_items.append((item, price))
            
    if not sellable_items:
        msg = "판매할 수 있는 비장착 아이템이 없습니다." if lang == "Korean" else "No unequipped items available to sell."
        print(cli_styles.red(f"\n{msg}"))
        return False
        
    lines = []
    for i, (item, price) in enumerate(sellable_items, 1):
        lines.append(f"{i}. {item} - Sell Price: {price} GP")
        
    cli_styles.draw_box(title, lines, cli_styles.YELLOW)
    
    prompt = "판매할 아이템 번호를 입력하세요 (취소하려면 엔터): " if lang == "Korean" else "Enter item number to sell (or press Enter to cancel): "
    choice = input(prompt).strip()
    
    if not choice:
        return False
        
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(sellable_items):
            item_name, price = sellable_items[idx]
            state['inventory'].remove(item_name)
            state['gold'] = state.get('gold', 0) + price
            
            success_msg = f"[성공] {item_name}을(를) {price} GP에 판매했습니다!" if lang == "Korean" else f"[Success] Sold {item_name} for {price} GP!"
            print(cli_styles.green(f"\n{success_msg}"))
            return True
        else:
            print(cli_styles.red("\nInvalid index."))
    except ValueError:
        print(cli_styles.red("\nPlease enter a valid number."))
        
    return False