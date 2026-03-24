from game_state import load_save, save_game, load_game_data
from gm_engine import generate_gm_response
import character
import combat
import actions

def main():
    print("=== CLI TRPG ENGINE: AUTO-DM UPGRADE ===")
    state = load_save()
    game_data = load_game_data()
    
    if not state:
        state = character.create_character()
        save_game(state)
    else:
        print(f"\nWelcome back, {state['name']}! Resuming your adventure...\n")

    initial_action = "Look around and assess the situation."
    
    while True:
        print("\n[The GM is processing the world...]\n")
        try:
            # gm_data is now a dictionary, not just a block of text
            gm_data = generate_gm_response(state, initial_action, game_data)
            
            # 1. Update the local save file instantly with the AI's math
            state['hp'] = gm_data['updated_hp']
            state['inventory'] = gm_data['updated_inventory']
            state['location'] = gm_data['updated_location']
            
            gained_xp = gm_data.get('awarded_xp', 0)
            character.check_level_up(state, gained_xp)
            
            # 2. Print the UI
            print(f"📍 Location: {state['location']}")
            print(f"❤️  HP: {state['hp']} | 🎒 Inventory: {', '.join(state['inventory'])} | ✨ XP: {state.get('xp', 0)}/{state['level']*100}")
            print("-" * 50)
            print(gm_data['narrative'])
            if gained_xp > 0:
                print(f"\n[You gained {gained_xp} XP!]")
            print("-" * 50)
            
            # --- LOCAL COMBAT INTERCEPT ---
            if gm_data.get('situation_type') == 'combat_start' and gm_data.get('spawned_monsters'):
                survived, initial_action = combat.handle_combat(state, game_data, gm_data)
                if not survived:
                    print("\n💀 YOU HAVE FALLEN IN BATTLE. Game Over.")
                    return
                save_game(state)
                continue

            # 3. Print the choices neatly
            for i, choice in enumerate(gm_data['choices'], 1):
                print(f"{i}. {choice}")
            
        except Exception as e:
            print(f"\n[API ERROR]: {e}")
            break
        
        print("\n" + "="*50)
        
        while True:
            action = input("\nWhat do you do? (Type 1, 2, 3, 'status', 'equip', 'shop', 'quit', or a custom action): ")
            
            if action.lower() == 'quit':
                print("Saving and exiting...")
                return
            
            if action.lower() in ['status', 'inventory', 'stats']:
                actions.show_status(state)
                continue
            
            if action.lower() == 'shop':
                if actions.handle_shop(state, game_data): save_game(state)
                continue
            
            if action.lower() == 'equip':
                if actions.handle_equip(state): save_game(state)
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