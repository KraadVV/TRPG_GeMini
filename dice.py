import re
import random

def get_modifier(stat_score):
    """Calculates the standard D&D ability modifier (e.g., 14 -> 2)."""
    return (stat_score - 10) // 2

def roll_from_string(description, default_val=1):
    """Parses strings like '2d4+2' and returns the total rolled."""
    if not description: return default_val
    match = re.search(r'(\d+)d(\d+)\+?(\d*)', description.lower())
    if match:
        return sum(random.randint(1, int(match.group(2))) for _ in range(int(match.group(1)))) + (int(match.group(3)) if match.group(3) else 0)
    return default_val