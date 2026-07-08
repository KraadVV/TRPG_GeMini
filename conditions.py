"""DnD 5e conditions system."""

CONDITIONS = {
    'blinded': {
        'name': 'Blinded',
        'description': 'Auto-fails sight checks. Attacks have disadvantage. Attacks against have advantage.',
        'effects': {
            'attack_disadvantage': True,
            'attacked_advantage': True,
            'auto_fail_sight_checks': True,
        }
    },
    'charmed': {
        'name': 'Charmed',
        'description': 'Cannot attack the charmer. Charmer has advantage on social checks.',
        'effects': {
            'cannot_attack_source': True,
            'social_advantage_to_source': True,
        }
    },
    'deafened': {
        'name': 'Deafened',
        'description': 'Auto-fails hearing checks.',
        'effects': {
            'auto_fail_hearing_checks': True,
        }
    },
    'frightened': {
        'name': 'Frightened',
        'description': 'Disadvantage on ability checks and attack rolls while source is in sight.',
        'effects': {
            'attack_disadvantage': True,
            'ability_check_disadvantage': True,
            'cannot_approach_source': True,
        }
    },
    'grappled': {
        'name': 'Grappled',
        'description': 'Speed is 0.',
        'effects': {
            'speed_zero': True,
        }
    },
    'incapacitated': {
        'name': 'Incapacitated',
        'description': 'Cannot take actions or reactions.',
        'effects': {
            'no_actions': True,
            'no_reactions': True,
        }
    },
    'invisible': {
        'name': 'Invisible',
        'description': 'Attacks have advantage. Attacks against have disadvantage.',
        'effects': {
            'attack_advantage': True,
            'attacked_disadvantage': True,
        }
    },
    'paralyzed': {
        'name': 'Paralyzed',
        'description': 'Incapacitated. Auto-fails STR/DEX saves. Attacks against have advantage. Melee attacks against auto-crit.',
        'effects': {
            'no_actions': True,
            'no_reactions': True,
            'auto_fail_str_dex_saves': True,
            'attacked_advantage': True,
            'melee_auto_crit': True,
        }
    },
    'petrified': {
        'name': 'Petrified',
        'description': 'Incapacitated. Auto-fails STR/DEX saves. Attacks against have advantage. Resistance to all damage.',
        'effects': {
            'no_actions': True,
            'no_reactions': True,
            'auto_fail_str_dex_saves': True,
            'attacked_advantage': True,
            'damage_resistance_all': True,
        }
    },
    'poisoned': {
        'name': 'Poisoned',
        'description': 'Disadvantage on attack rolls and ability checks.',
        'effects': {
            'attack_disadvantage': True,
            'ability_check_disadvantage': True,
        }
    },
    'prone': {
        'name': 'Prone',
        'description': 'Attacks have disadvantage. Melee attacks against have advantage. Ranged attacks against have disadvantage.',
        'effects': {
            'attack_disadvantage': True,
            'melee_attacked_advantage': True,
            'ranged_attacked_disadvantage': True,
        }
    },
    'restrained': {
        'name': 'Restrained',
        'description': 'Speed 0. Attacks have disadvantage. Attacks against have advantage. DEX saves have disadvantage.',
        'effects': {
            'speed_zero': True,
            'attack_disadvantage': True,
            'attacked_advantage': True,
            'dex_save_disadvantage': True,
        }
    },
    'stunned': {
        'name': 'Stunned',
        'description': 'Incapacitated. Auto-fails STR/DEX saves. Attacks against have advantage.',
        'effects': {
            'no_actions': True,
            'no_reactions': True,
            'auto_fail_str_dex_saves': True,
            'attacked_advantage': True,
        }
    },
    'unconscious': {
        'name': 'Unconscious',
        'description': 'Incapacitated. Drops items. Auto-fails STR/DEX saves. Attacks against have advantage. Melee attacks against auto-crit.',
        'effects': {
            'no_actions': True,
            'no_reactions': True,
            'drop_items': True,
            'auto_fail_str_dex_saves': True,
            'attacked_advantage': True,
            'melee_auto_crit': True,
        }
    },
}

def add_condition(entity, condition_name, duration=None, source=None):
    """Adds a condition to an entity's 'conditions' list."""
    if 'conditions' not in entity or entity['conditions'] is None:
        entity['conditions'] = []
    
    condition_name = condition_name.lower().strip()
    if condition_name not in CONDITIONS:
        return
    
    # Avoid duplicate conditions
    existing = [c for c in entity['conditions'] if c.get('name', '').lower() == condition_name]
    if existing:
        # Update duration if the new duration is longer or if the existing one is not permanent
        current_dur = existing[0].get('duration')
        if duration is not None:
            if current_dur is None or duration > current_dur:
                existing[0]['duration'] = duration
        return
    
    entity['conditions'].append({
        'name': CONDITIONS[condition_name]['name'],
        'duration': duration,  # number of rounds, or None for indefinite
        'source': source       # entity name that caused the condition
    })

def remove_condition(entity, condition_name):
    """Removes a condition from an entity's 'conditions' list."""
    if 'conditions' not in entity or not entity['conditions']:
        return
    condition_name = condition_name.lower().strip()
    entity['conditions'] = [c for c in entity['conditions'] if c.get('name', '').lower() != condition_name]

def tick_conditions(entity):
    """Ticks down condition durations by 1 round. Returns a list of expired condition names."""
    if 'conditions' not in entity or not entity['conditions']:
        return []
    
    expired = []
    remaining = []
    for cond in entity['conditions']:
        duration = cond.get('duration')
        if duration is not None:
            duration -= 1
            if duration <= 0:
                expired.append(cond['name'])
                continue
            cond['duration'] = duration
        remaining.append(cond)
    
    entity['conditions'] = remaining
    return expired

def has_condition(entity, condition_name):
    """Returns True if the entity has the specified condition."""
    if 'conditions' not in entity or not entity['conditions']:
        return False
    condition_name = condition_name.lower().strip()
    return any(c.get('name', '').lower() == condition_name for c in entity['conditions'])

def get_active_conditions(entity):
    """Returns list of active condition names."""
    if 'conditions' not in entity or not entity['conditions']:
        return []
    return [c['name'] for c in entity['conditions']]

def has_effect(entity, effect_name):
    """Returns True if any of the entity's conditions grant the specified effect."""
    if 'conditions' not in entity or not entity['conditions']:
        return False
    for cond in entity['conditions']:
        c_name = cond.get('name', '').lower()
        if c_name in CONDITIONS:
            if CONDITIONS[c_name]['effects'].get(effect_name, False):
                return True
    return False

def can_act(entity):
    """Returns True if the entity is capable of taking actions."""
    return not has_effect(entity, 'no_actions')

def can_react(entity):
    """Returns True if the entity is capable of taking reactions."""
    return not has_effect(entity, 'no_reactions')
