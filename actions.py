import re
import random
import dice

def show_status(state):
    print("\n=== CHARACTER STATUS ===")
    print(f"Name: {state['name']}")
    print(f"Race: {state.get('race', 'Unknown')} | Class: {state.get('class', 'Unknown')} | Background: {state.get('background', 'Unknown')} | Level: {state['level']} (XP: {state.get('xp', 0)}/{state['level']*100})")
    print(f"Appearance: {state.get('appearance', 'Not specified')}")
    print(f"Backstory: {state.get('backstory', 'Not specified')}")
    if state.get('max_mp', 0) > 0:
        print(f"HP: {state['hp']}/{state.get('max_hp', state['hp'])} | MP: {state.get('mp', 0)}/{state.get('max_mp', 0)} | AC: {state.get('ac', 10)} | Gold: {state.get('gold', 0)} GP")
    else:
        print(f"HP: {state['hp']}/{state.get('max_hp', state['hp'])} | AC: {state.get('ac', 10)} | Gold: {state.get('gold', 0)} GP")
    if 'stats' in state:
        s = state['stats']
        print(f"STR: {s['STR']} | DEX: {s['DEX']} | CON: {s['CON']} | INT: {s['INT']} | WIS: {s['WIS']} | CHA: {s['CHA']}")
    print(f"Equipped: [Weapon: {state.get('equipped_weapon', 'None')}] [Armor: {state.get('equipped_armor', 'None')}]")
    print(f"Location: {state['location']}")
    if state.get('companions'):
        print(f"Companions: {', '.join(state['companions'])}")
    print(f"Inventory: {', '.join(state['inventory'])}")
    if state.get('spells'):
        print(f"Known Spells: {', '.join(state['spells'])}")
    print("========================")

def handle_shop(state, game_data):
    print("\n=== LOCAL SHOP ===")
    print(f"Your Gold: {state.get('gold', 0)} GP")
    items = game_data.get("items", {})
    for item, details in items.items():
        print(f"- {item}: {details['price']} GP ({details['description']})")
    buy_choice = input("\nEnter the name of the item to buy (or press Enter to cancel): ").title()
    if buy_choice in items:
        price = items[buy_choice]["price"]
        if state.get("gold", 0) >= price:
            state["gold"] = state.get("gold", 0) - price
            state["inventory"].append(buy_choice)
            print(f"\n[Success] You bought a {buy_choice} for {price} GP!")
            return True
        else: print("\n[Failed] Not enough gold!")
    return False

def handle_equip(state, game_data):
    print("\n=== EQUIP ITEM ===")
    print(f"Inventory: {', '.join(state['inventory'])}")
    item_to_equip = input("Enter the name of the item to equip (or press Enter to cancel): ").title()
    if item_to_equip in state['inventory']:
        slot = input("Equip as (W)eapon or (A)rmor? ").lower()
        if slot == 'w': 
            state['equipped_weapon'] = item_to_equip
            print(f"Equipped {item_to_equip} as your weapon.")
            return True
        elif slot == 'a': 
            state['equipped_armor'] = item_to_equip
            print(f"Equipped {item_to_equip} as your armor.")
            
            # Calculate new AC
            dex_mod = dice.get_modifier(state['stats'].get('DEX', 10))
            base_ac = 10
            item_info = game_data.get('items', {}).get(item_to_equip)
            if item_info:
                ac_match = re.search(r'AC (\d+)', item_info.get('description', ''))
                if ac_match:
                    base_ac = int(ac_match.group(1))
            state['ac'] = base_ac + dex_mod
            print(f"Your AC is now {state['ac']}.")
            return True
    elif item_to_equip:
        print("\n[Failed] You don't have that item in your inventory.")
    return False

def handle_use(state, game_data):
    print("\n=== USE ITEM ===")
    print(f"Inventory: {', '.join(state['inventory'])}")
    item_to_use = input("Enter the name of the item to use (or press Enter to cancel): ").title()
    
    if item_to_use in state['inventory']:
        item_info = game_data.get('items', {}).get(item_to_use)
        if item_info and ('Heal' in item_info['description'] or 'heal' in item_info['description'].lower()):
            desc = item_info['description']
            heal_amount = dice.roll_from_string(desc, default_val=5)
            
            old_hp = state['hp']
            state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + heal_amount)
            healed = state['hp'] - old_hp
            state['inventory'].remove(item_to_use)
            print(f"\n[Success] You consumed the {item_to_use} and recovered {healed} HP! (Current HP: {state['hp']}/{state['max_hp']})")
            return True
        else:
            print(f"\n[Failed] {item_to_use} cannot be used this way or is not a known consumable.")
    elif item_to_use:
        print("\n[Failed] You don't have that item in your inventory.")
    return False

def handle_rest(state):
    print("\n=== REST ===")
    print("1. Short Rest (Heal half of your Max HP, can be done anywhere)")
    print("2. Long Rest (Heal to full HP, requires a safe location)")
    choice = input("Choose a rest type (1/2, or press Enter to cancel): ")
    
    if choice == '1':
        heal_amount = max(1, state.get('max_hp', 10) // 2)
        old_hp = state['hp']
        state['hp'] = min(state.get('max_hp', state['hp']), state['hp'] + heal_amount)
        if state.get('max_mp', 0) > 0: state['mp'] = min(state['max_mp'], state.get('mp', 0) + (state['max_mp'] // 2))
        print(f"\n[Success] You took a short rest and recovered {state['hp'] - old_hp} HP! (Current HP: {state['hp']}/{state['max_hp']})")
        return True
    elif choice == '2':
        if state.get('is_safe', False) or state.get('can_shop', False):
            state['hp'] = state.get('max_hp', state['hp'])
            if state.get('max_mp', 0) > 0: state['mp'] = state['max_mp']
            print(f"\n[Success] You took a long rest in a safe place. You are fully healed! (Current HP: {state['hp']}/{state['max_hp']})")
            return True
        else:
            print("\n[Failed] It's too dangerous to take a Long Rest here! Find a town, inn, or secure camp.")
    return False