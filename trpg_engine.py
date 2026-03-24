import random
from game_state import load_save, save_game
from gm_engine import generate_gm_response

def main():
    print("=== CLI TRPG ENGINE: AUTO-DM UPGRADE ===")
    state = load_save()
    
    if not state:
        print("\nNo save file found. Let's create a new D&D character!")
        name = input("Enter your character's name: ")
        race = input("Choose your race (e.g., Human, Elf, Dwarf, Orc): ")
        char_class = input("Choose your class (e.g., Fighter, Wizard, Rogue, Cleric): ")
        
        print("\nHow would you like to generate your Ability Scores?")
        print("1. Manual  (Enter them yourself)")
        print("2. Proper  (Optimized for your chosen class)")
        print("3. Chaotic (Completely randomized 3-18)")
        print("4. Natural (Optimized base with random +/- variations)")
        stat_choice = input("Choose a method (1/2/3/4): ")
        
        def get_proper_stats(c_class):
            c = c_class.lower()
            if any(x in c for x in ['fighter', 'barbarian', 'paladin']): return {"STR": 15, "DEX": 13, "CON": 14, "INT": 8, "WIS": 12, "CHA": 10}
            elif any(x in c for x in ['wizard', 'sorcerer', 'artificer']): return {"STR": 8, "DEX": 14, "CON": 13, "INT": 15, "WIS": 12, "CHA": 10}
            elif any(x in c for x in ['rogue', 'ranger', 'monk']): return {"STR": 8, "DEX": 15, "CON": 13, "INT": 14, "WIS": 10, "CHA": 12}
            elif any(x in c for x in ['cleric', 'druid']): return {"STR": 13, "DEX": 8, "CON": 14, "INT": 10, "WIS": 15, "CHA": 12}
            elif any(x in c for x in ['bard', 'warlock']): return {"STR": 8, "DEX": 13, "CON": 12, "INT": 10, "WIS": 14, "CHA": 15}
            return {"STR": 12, "DEX": 12, "CON": 12, "INT": 12, "WIS": 12, "CHA": 12}

        if stat_choice == '2':
            stats = get_proper_stats(char_class)
        elif stat_choice == '3':
            stats = {s: random.randint(3, 18) for s in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        elif stat_choice == '4':
            base = get_proper_stats(char_class)
            stats = {s: max(3, min(20, val + random.randint(-2, 2))) for s, val in base.items()}
        else:
            print("\nEnter your Ability Scores (typically 8-20). Default is 10 if left blank.")
            def get_stat(stat_name):
                try:
                    val = input(f"{stat_name}: ")
                    return int(val) if val.strip() else 10
                except ValueError:
                    return 10
            stats = {"STR": get_stat("Strength"), "DEX": get_stat("Dexterity"), "CON": get_stat("Constitution"), "INT": get_stat("Intelligence"), "WIS": get_stat("Wisdom"), "CHA": get_stat("Charisma")}
        
        weapon = input("\nChoose your starting weapon (e.g., Longsword, Wooden Staff, Dagger): ")
        
        # Calculate standard starting HP (Base 10 + Constitution modifier)
        con_mod = (stats["CON"] - 10) // 2
        max_hp = max(1, 10 + con_mod)
        
        state = {
            "name": name,
            "race": race,
            "class": char_class,
            "hp": max_hp,
            "max_hp": max_hp,
            "level": 1,
            "stats": stats,
            "inventory": [weapon, "Adventurer's Pack", "Health Potion"],
            "location": "The Crossroads",
            "history": []
        }
        save_game(state)
        print(f"\nWelcome, {name} the {race} {char_class}! Your adventure begins now.\n")
    else:
        print(f"\nWelcome back, {state['name']}! Resuming your adventure...\n")

    initial_action = "Look around and assess the situation."
    
    while True:
        print("\n[The GM is processing the world...]\n")
        try:
            # gm_data is now a dictionary, not just a block of text
            gm_data = generate_gm_response(state, initial_action)
            
            # 1. Update the local save file instantly with the AI's math
            state['hp'] = gm_data['updated_hp']
            state['inventory'] = gm_data['updated_inventory']
            state['location'] = gm_data['updated_location']
            
            # 2. Print the UI
            print(f"📍 Location: {state['location']}")
            print(f"❤️  HP: {state['hp']} | 🎒 Inventory: {', '.join(state['inventory'])}")
            print("-" * 50)
            print(gm_data['narrative'])
            print("-" * 50)
            
            # 3. Print the choices neatly
            for i, choice in enumerate(gm_data['choices'], 1):
                print(f"{i}. {choice}")
            
        except Exception as e:
            print(f"\n[API ERROR]: {e}")
            break
        
        print("\n" + "="*50)
        
        while True:
            action = input("\nWhat do you do? (Type 1, 2, 3, 'status', 'quit', or a custom action): ")
            
            if action.lower() == 'quit':
                print("Saving and exiting...")
                return
            
            if action.lower() in ['status', 'inventory', 'stats']:
                print("\n=== CHARACTER STATUS ===")
                print(f"Name: {state['name']}")
                print(f"Race: {state.get('race', 'Unknown')} | Class: {state.get('class', 'Unknown')} | Level: {state['level']}")
                print(f"HP: {state['hp']}/{state.get('max_hp', state['hp'])}")
                if 'stats' in state:
                    s = state['stats']
                    print(f"STR: {s['STR']} | DEX: {s['DEX']} | CON: {s['CON']} | INT: {s['INT']} | WIS: {s['WIS']} | CHA: {s['CHA']}")
                print(f"Location: {state['location']}")
                print(f"Inventory: {', '.join(state['inventory'])}")
                print("========================")
                continue
            
            # If the user typed a number, map it to the actual choice string
            if action in ['1', '2', '3']:
                initial_action = gm_data['choices'][int(action) - 1]
            else:
                initial_action = action
            
            break
        
        state["history"].append(initial_action)
        if len(state["history"]) > 5:
            state["history"].pop(0) 
            
        save_game(state)

if __name__ == "__main__":
    main()