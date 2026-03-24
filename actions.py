def show_status(state):
    print("\n=== CHARACTER STATUS ===")
    print(f"Name: {state['name']}")
    print(f"Race: {state.get('race', 'Unknown')} | Class: {state.get('class', 'Unknown')} | Level: {state['level']} (XP: {state.get('xp', 0)}/{state['level']*100})")
    print(f"HP: {state['hp']}/{state.get('max_hp', state['hp'])} | AC: {state.get('ac', 10)} | Gold: {state.get('gold', 0)} GP")
    if 'stats' in state:
        s = state['stats']
        print(f"STR: {s['STR']} | DEX: {s['DEX']} | CON: {s['CON']} | INT: {s['INT']} | WIS: {s['WIS']} | CHA: {s['CHA']}")
    print(f"Equipped: [Weapon: {state.get('equipped_weapon', 'None')}] [Armor: {state.get('equipped_armor', 'None')}]")
    print(f"Location: {state['location']}")
    print(f"Inventory: {', '.join(state['inventory'])}")
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

def handle_equip(state):
    print("\n=== EQUIP ITEM ===")
    print(f"Inventory: {', '.join(state['inventory'])}")
    item_to_equip = input("Enter the name of the item to equip (or press Enter to cancel): ").title()
    if item_to_equip in state['inventory']:
        slot = input("Equip as (W)eapon or (A)rmor? ").lower()
        if slot == 'w': state['equipped_weapon'] = item_to_equip; print(f"Equipped {item_to_equip} as your weapon."); return True
        elif slot == 'a': state['equipped_armor'] = item_to_equip; print(f"Equipped {item_to_equip} as your armor."); return True
    elif item_to_equip:
        print("\n[Failed] You don't have that item in your inventory.")
    return False