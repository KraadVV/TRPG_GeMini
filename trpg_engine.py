from game_state import load_save, save_game
from gm_engine import generate_gm_response

def main():
    print("=== CLI TRPG ENGINE: AUTO-DM UPGRADE ===")
    state = load_save()
    
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
                print(f"Name: {state['name']} (Level {state['level']})")
                print(f"HP: {state['hp']}")
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