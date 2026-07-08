"""DnD 5e Class Features definition."""

CLASS_FEATURES = {
    'Fighter': {
        1: [
            {
                'name': 'Second Wind',
                'type': 'bonus_action',
                'uses_per': 'short_rest',
                'max_uses': 1,
                'description': 'Use a bonus action to recover 1d10 + Fighter level HP.'
            }
        ],
        2: [
            {
                'name': 'Action Surge',
                'type': 'special',
                'uses_per': 'short_rest',
                'max_uses': 1,
                'description': 'Take one additional action on your turn.'
            }
        ],
    },
    'Rogue': {
        1: [
            {
                'name': 'Sneak Attack',
                'type': 'passive',
                'description': 'Deal extra damage once per turn to a target you hit with advantage or if an ally is within 5 feet.'
            }
        ],
    },
    'Wizard': {
        1: [
            {
                'name': 'Arcane Recovery',
                'type': 'special',
                'uses_per': 'long_rest',
                'max_uses': 1,
                'description': 'Recover some spent spell slots during a short rest.'
            }
        ]
    },
    'Cleric': {
        1: [
            {
                'name': 'Divine Domain',
                'type': 'passive',
                'description': 'Your domain defines your cleric subclass and focus.'
            }
        ]
    },
    'Bard': {
        1: [
            {
                'name': 'Bardic Inspiration',
                'type': 'bonus_action',
                'uses_per': 'long_rest',
                'description': 'Inspire others with a d6, adding to their checks/attacks/saves.'
            }
        ]
    }
}

def get_features_at_level(char_class, level):
    class_data = CLASS_FEATURES.get(char_class, {})
    features = []
    for lvl in range(1, level + 1):
        if lvl in class_data:
            features.extend(class_data[lvl])
    return features
