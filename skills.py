import random
import dice
import cli_styles
import conditions
import skills_data

def handle_skill_check(state, gm_data):
    lang = state.get('language', 'Korean')
    
    skill_name = gm_data.get('required_skill')  # e.g., "Stealth"
    stat = gm_data.get('required_roll')
    
    if skill_name in skills_data.SKILLS:
        stat = skills_data.SKILLS[skill_name]
    else:
        skill_name = None
        
    # Fallback if the AI provides an invalid stat abbreviation
    if stat not in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        stat = "DEX"
        
    display_name = skill_name if skill_name else stat
    title = f"🎲 능력치 판정 요구: {display_name} (난이도 DC {gm_data.get('difficulty_class', 10)}) 🎲" if lang == "Korean" else f"🎲 SKILL CHECK: {display_name} (DC {gm_data.get('difficulty_class', 10)}) 🎲"
    
    has_adv = gm_data.get('advantage', False)
    has_dis = gm_data.get('disadvantage', False) or conditions.has_effect(state, 'ability_check_disadvantage')
    if state.get('armor_penalty') and stat in ['STR', 'DEX']:
        has_dis = True
    
    info_lines = []
    if has_adv and not has_dis:
        info_lines.append("유리함 (Advantage) 적용!" if lang == "Korean" else "Advantage applies!")
    elif has_dis and not has_adv:
        info_lines.append("불리함 (Disadvantage) 적용!" if lang == "Korean" else "Disadvantage applies!")
        
    lines = [
        f"The GM demands a {display_name} check to proceed.",
        "주사위를 굴려 운명을 시험해 봅시다!" if lang == "Korean" else "Roll a d20 and add your modifier."
    ] + info_lines
    cli_styles.draw_box(title, lines, cli_styles.PURPLE)
    
    prompt = "엔터를 눌러 주사위(d20)를 굴리세요..." if lang == "Korean" else "Press Enter to roll a d20..."
    input(prompt)
    
    roll, roll_detail = dice.roll_d20(advantage=has_adv, disadvantage=has_dis)
    modifier = dice.get_modifier(state['stats'][stat])
    
    # Calculate proficiency/expertise bonus
    prof_bonus = 0
    bonus_type = ""
    level_prof = 2 + ((state.get('level', 1) - 1) // 4)
    
    if skill_name:
        if skill_name in state.get('expertise', []):
            prof_bonus = level_prof * 2
            bonus_type = " (Expertise)"
        elif skill_name in state.get('skill_proficiencies', []):
            prof_bonus = level_prof
            bonus_type = " (Proficient)"
            
    # Jack of all trades for Bard
    if prof_bonus == 0 and state.get('class') == 'Bard':
        prof_bonus = level_prof // 2
        bonus_type = " (Jack of All Trades)"
        
    total = roll + modifier + prof_bonus
    dc = gm_data.get('difficulty_class', 10)
    
    bonus_str = f" + {prof_bonus}{bonus_type}" if prof_bonus > 0 else ""
    roll_result = f"🎲 Roll: {cli_styles.yellow(roll_detail)} + {cli_styles.cyan(f'{modifier} ({stat})')}{cli_styles.purple(bonus_str)} = {cli_styles.bold(str(total))} vs DC {dc}"
    print(f"\n{roll_result}")
    
    if total >= dc:
        print(cli_styles.green(cli_styles.bold("\n✅ SUCCESS! / 판정 성공!")))
        
        if lang == "Korean":
            return f"내가 난이도 {dc}의 {display_name} 판정에서 주사위 {total}을(를) 굴려 성공했다!"
        return f"I rolled a {total} for my {display_name} check against a DC of {dc}, and I succeeded!"
    else:
        print(cli_styles.red(cli_styles.bold("\n❌ FAILURE... / 판정 실패...")))
        
        if lang == "Korean":
            return f"내가 난이도 {dc}의 {display_name} 판정에서 주사위 {total}을(를) 굴려 실패했다..."
        return f"I rolled a {total} for my {display_name} check against a DC of {dc}, and I failed."