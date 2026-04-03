import random
import dice

def get_proper_stats(c_class):
    c = c_class.lower()
    if any(x in c for x in ['fighter', 'barbarian', 'paladin']): return {"STR": 15, "DEX": 13, "CON": 14, "INT": 8, "WIS": 12, "CHA": 10}
    elif any(x in c for x in ['wizard', 'sorcerer', 'artificer']): return {"STR": 8, "DEX": 14, "CON": 13, "INT": 15, "WIS": 12, "CHA": 10}
    elif any(x in c for x in ['rogue', 'ranger', 'monk']): return {"STR": 8, "DEX": 15, "CON": 13, "INT": 14, "WIS": 10, "CHA": 12}
    elif any(x in c for x in ['cleric', 'druid']): return {"STR": 13, "DEX": 8, "CON": 14, "INT": 10, "WIS": 15, "CHA": 12}
    elif any(x in c for x in ['bard', 'warlock']): return {"STR": 8, "DEX": 13, "CON": 12, "INT": 10, "WIS": 14, "CHA": 15}
    return {"STR": 12, "DEX": 12, "CON": 12, "INT": 12, "WIS": 12, "CHA": 12}

def create_character():
    print("\nNo save file found. Let's create a new D&D character!")
    name = input("Enter your character's name: ")
    
    print("\n--- Choose Your Heritage ---")
    print("Your race grants you unique physical traits and cultural backgrounds.")
    print("- Human: Adaptable, ambitious, and diverse, found in every corner of the world.")
    print("- Elf: Graceful, long-lived, and attuned to the magical weave of nature.")
    print("- Dwarf: Hardy and traditional, known for their resilience and skill in crafting.")
    print("- Orc (or Half-Orc): Fierce and strong warriors with a culture deeply tied to survival and honor.")
    print("- Halfling: Small and lucky folk who prefer peace, comfort, and sometimes stealth.")
    print("- Dragonborn: Proud draconic humanoids with a potent breath weapon and strong clan loyalties.")
    race = input("Choose your race (or type another of your choice): ")
    
    print("\n--- Choose Your Path ---")
    print("In the world of D&D, you can choose your class to define your skills and combat style.")
    print("- Fighter: Masters of martial combat, skilled with a variety of weapons and armor.")
    print("- Rogue: Stealthy tricksters who rely on precision, stealth, and exploiting enemy weaknesses.")
    print("- Wizard: Scholarly magic-users capable of manipulating the structures of reality.")
    print("- Cleric: Priestly champions who wield divine magic in service of a higher power.")
    print("- Bard: Inspiring magicians whose power echoes the music of creation. Sometimes, bards use their charm to avoid fights entirely.")
    print("- Paladin: Holy warriors bound to a sacred oath, blending martial prowess with divine magic.")
    char_class = input("Choose your class: ")
    
    print("\n--- Narrative Details ---")
    background = input("Enter your character's background (e.g., Soldier, Criminal, Noble, Acolyte): ")
    appearance = input("Describe your character's appearance: ")
    backstory = input("Write a brief backstory for your character: ")
    
    print("\nHow would you like to generate your Ability Scores?")
    print("1. Manual  (Enter them yourself)")
    print("2. Proper  (Optimized for your chosen class)")
    print("3. Chaotic (Completely randomized 3-18)")
    print("4. Natural (Optimized base with random +/- variations)")
    stat_choice = input("Choose a method (1/2/3/4): ")
    
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
    
    con_mod = dice.get_modifier(stats["CON"])
    max_hp = max(1, 10 + con_mod)
    dex_mod = dice.get_modifier(stats["DEX"])
    
    c_lower = char_class.lower()
    if any(x in c_lower for x in ['wizard', 'sorcerer', 'warlock']):
        max_mp = 10 + dice.get_modifier(stats["INT"] if 'wizard' in c_lower else stats["CHA"])
    elif any(x in c_lower for x in ['cleric', 'druid', 'bard']):
        max_mp = 10 + dice.get_modifier(stats["WIS"] if 'cleric' in c_lower or 'druid' in c_lower else stats["CHA"])
    elif any(x in c_lower for x in ['paladin', 'ranger']):
        max_mp = 5
    else:
        max_mp = 0

    state = {
        "name": name, "race": race, "class": char_class,
        "background": background, "appearance": appearance, "backstory": backstory,
        "ac": 10 + dex_mod,
        "equipped_weapon": weapon, "equipped_armor": "None",
        "hp": max_hp, "max_hp": max_hp, "level": 1, "xp": 0, "gold": 50,
        "mp": max_mp, "max_mp": max_mp, "spells": [],
        "stats": stats, "inventory": [weapon, "Adventurer's Pack", "Health Potion"],
        "location": "The Town", "history": [], "companions": []
    }
    print(f"\nWelcome, {name} the {race} {char_class}! Your adventure begins now.\n")
    return state

def check_level_up(state, gained_xp):
    state['xp'] = state.get('xp', 0) + gained_xp
    xp_needed = state['level'] * 100
    if state['xp'] >= xp_needed:
        state['xp'] -= xp_needed
        state['level'] += 1
        hp_increase = max(1, 5 + dice.get_modifier(state['stats']['CON']))
        state['max_hp'] += hp_increase
        state['hp'] = state['max_hp']
        
        if state.get('max_mp', 0) > 0:
            state['max_mp'] += max(1, 2 + dice.get_modifier(state['stats']['INT']))
            state['mp'] = state['max_mp']
            
        print(f"\n🎉 LEVEL UP! You are now Level {state['level']}! 🎉\nMax HP increased by {hp_increase}.")
        while True:
            stat_up = input("Choose a stat to increase by 1 (STR, DEX, CON, INT, WIS, CHA): ").upper()
            if stat_up in state['stats']:
                state['stats'][stat_up] += 1
                print(f"Your {stat_up} is now {state['stats'][stat_up]}!")
                break
            print("Invalid stat. Please try again.")