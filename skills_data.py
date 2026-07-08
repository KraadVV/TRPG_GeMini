"""DnD 5e Skills, Races, and Class data."""

SKILLS = {
    'Athletics': 'STR',
    'Acrobatics': 'DEX',
    'Sleight of Hand': 'DEX',
    'Stealth': 'DEX',
    'Arcana': 'INT',
    'History': 'INT',
    'Investigation': 'INT',
    'Nature': 'INT',
    'Religion': 'INT',
    'Animal Handling': 'WIS',
    'Insight': 'WIS',
    'Medicine': 'WIS',
    'Perception': 'WIS',
    'Survival': 'WIS',
    'Deception': 'CHA',
    'Intimidation': 'CHA',
    'Performance': 'CHA',
    'Persuasion': 'CHA',
}

CLASS_SKILL_OPTIONS = {
    'Fighter': {
        'count': 2,
        'choices': ['Acrobatics', 'Animal Handling', 'Athletics', 'History', 'Insight', 'Intimidation', 'Perception', 'Survival']
    },
    'Rogue': {
        'count': 4,
        'choices': ['Acrobatics', 'Athletics', 'Deception', 'Insight', 'Intimidation', 'Investigation', 'Perception', 'Performance', 'Persuasion', 'Sleight of Hand', 'Stealth']
    },
    'Wizard': {
        'count': 2,
        'choices': ['Arcana', 'History', 'Insight', 'Investigation', 'Medicine', 'Religion']
    },
    'Cleric': {
        'count': 2,
        'choices': ['History', 'Insight', 'Medicine', 'Persuasion', 'Religion']
    },
    'Bard': {
        'count': 3,
        'choices': list(SKILLS.keys())
    },
}

RACE_SKILL_BONUSES = {
    'Elf': ['Perception'],
    'Orc': ['Intimidation'], # Orc / Half-Orc
}

CLASS_SAVE_PROFICIENCIES = {
    'Fighter': ['STR', 'CON'],
    'Rogue': ['DEX', 'INT'],
    'Wizard': ['INT', 'WIS'],
    'Cleric': ['WIS', 'CHA'],
    'Bard': ['DEX', 'CHA'],
}

CLASS_ARMOR_PROFICIENCY = {
    'Fighter': ['light', 'medium', 'heavy', 'shield'],
    'Rogue': ['light'],
    'Wizard': [],
    'Cleric': ['light', 'medium', 'shield'],
    'Bard': ['light'],
}

CLASS_HIT_DICE = {
    'Fighter': 10,
    'Rogue': 8,
    'Wizard': 6,
    'Cleric': 8,
    'Bard': 8,
}

XP_THRESHOLDS = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000,
}

RACE_DATA = {
    'Human': {
        'stat_bonuses': {'STR': 1, 'DEX': 1, 'CON': 1, 'INT': 1, 'WIS': 1, 'CHA': 1},
        'traits': ['Versatile'],
        'speed': 30,
        'languages': ['Common'],
    },
    'Elf': {
        'stat_bonuses': {'DEX': 2},
        'traits': ['Darkvision', 'Fey Ancestry', 'Trance'],
        'speed': 30,
        'languages': ['Common', 'Elvish'],
    },
    'Dwarf': {
        'stat_bonuses': {'CON': 2},
        'traits': ['Darkvision', 'Dwarven Resilience', 'Stonecunning'],
        'speed': 25,
        'languages': ['Common', 'Dwarvish'],
    },
    'Orc': {
        'stat_bonuses': {'STR': 2, 'CON': 1},
        'traits': ['Darkvision', 'Relentless Endurance', 'Savage Attacks'],
        'speed': 30,
        'languages': ['Common', 'Orc'],
    },
    'Halfling': {
        'stat_bonuses': {'DEX': 2},
        'traits': ['Lucky', 'Brave', 'Halfling Nimbleness'],
        'speed': 25,
        'languages': ['Common', 'Halfling'],
    },
}

# Spell slots per level for Full Casters (Wizard, Cleric, Bard, Sorcerer, Druid)
FULL_CASTER_SLOTS = {
    1: {1: 2},
    2: {1: 3},
    3: {1: 4, 2: 2},
    4: {1: 4, 2: 3},
    5: {1: 4, 2: 3, 3: 2},
    6: {1: 4, 2: 3, 3: 3},
    7: {1: 4, 2: 3, 3: 3, 4: 1},
    8: {1: 4, 2: 3, 3: 3, 4: 2},
    9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
    10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
    13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
    15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
    17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
    18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
    19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
    20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
}

def get_slots_for_class_and_level(char_class, level):
    c_lower = char_class.lower()
    if any(x in c_lower for x in ['wizard', 'cleric', 'bard', 'sorcerer', 'druid']):
        return dict(FULL_CASTER_SLOTS.get(level, {1: 2}))
    elif any(x in c_lower for x in ['paladin', 'ranger']):
        if level < 2:
            return {}
        half_lvl = level // 2
        return dict(FULL_CASTER_SLOTS.get(half_lvl, {1: 2}))
    return {}
