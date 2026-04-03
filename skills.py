import random
import dice

def handle_skill_check(state, gm_data):
    stat = gm_data.get('required_roll')
    dc = gm_data.get('difficulty_class', 10)
    
    # Fallback if the AI provides an invalid stat abbreviation
    if stat not in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        stat = "DEX"
        
    print(f"\n🎲 === SKILL CHECK REQUIRED: {stat} (DC {dc}) === 🎲")
    input("Press Enter to roll a d20...")
    
    roll = random.randint(1, 20)
    modifier = dice.get_modifier(state['stats'][stat])
    total = roll + modifier
    
    print(f"\nYou rolled a {roll} + {modifier} ({stat} mod) = {total}.")
    
    if total >= dc:
        print("✅ Success!")
        return f"I rolled a {total} for my {stat} check against a DC of {dc}, and I succeeded!"
    else:
        print("❌ Failure!")
        return f"I rolled a {total} for my {stat} check against a DC of {dc}, and I failed."