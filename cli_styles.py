import sys
import re

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
DARK_GRAY = "\033[90m"

# Helper Functions to wrap text in colors
def bold(text): return f"{BOLD}{text}{RESET}"
def red(text): return f"{RED}{text}{RESET}"
def green(text): return f"{GREEN}{text}{RESET}"
def yellow(text): return f"{YELLOW}{text}{RESET}"
def blue(text): return f"{BLUE}{text}{RESET}"
def purple(text): return f"{PURPLE}{text}{RESET}"
def cyan(text): return f"{CYAN}{text}{RESET}"
def gray(text): return f"{DARK_GRAY}{text}{RESET}"

def draw_divider(char="─", length=60, color=CYAN):
    print(f"{color}{char * length}{RESET}")

def render_bar(val, max_val, bar_color=GREEN, length=15):
    if max_val <= 0: return ""
    percent = max(0, min(1.0, val / max_val))
    filled_length = int(round(length * percent))
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"{bar_color}[{bar}] {val}/{max_val}{RESET}"

def draw_box(title, content, border_color=CYAN, text_color=WHITE):
    """Draws a beautiful framed box around text."""
    if isinstance(content, str):
        lines = content.split('\n')
    else:
        lines = list(content)
        
    # Helper to calculate visual length ignoring ANSI escape codes
    def visual_len(text):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return len(ansi_escape.sub('', text))
        
    # Calculate visual width
    width = max(visual_len(title) + 4, 60)
    for line in lines:
        width = max(width, visual_len(line) + 4)
        
    # Header
    title_str = f" {title} "
    header = f"{border_color}┌─{bold(title_str)}{border_color}{'─' * (width - visual_len(title_str) - 2)}┐{RESET}"
    print(header)
    
    # Body
    for line in lines:
        stripped = line.rstrip()
        padding = width - visual_len(stripped)
        print(f"{border_color}│ {RESET}{text_color}{stripped}{' ' * (padding - 2)}{border_color}│{RESET}")
        
    # Footer
    print(f"{border_color}└{'─' * width}┘{RESET}")
