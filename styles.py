"""
styles.py

Define fonts and colors for consistent styling across the app.
"""

# Font definitions:
# - HEADER_FONT: large, bold font for main headers
# - NORMAL_FONT: standard font size for regular text
# - SMALL_FONT: slightly smaller font for captions or subtle text

HEADER_FONT = ("Helvetica Neue", 34, "bold")     # Main header font
NORMAL_FONT = ("Helvetica Neue", 16)             # Body text font
SMALL_FONT = ("Helvetica Neue", 14)              # Smaller text for notes or captions

# Tab widget color scheme:
# - TAB_BG/TAB_FG: background and text colors for inactive tabs
# - ACTIVE_TAB_BG/ACTIVE_TAB_FG: background and text colors for the currently active tab

TAB_BG = "#222"                   # Inactive tab background (dark gray)
TAB_FG = "#fff"                   # Inactive tab text (white)
ACTIVE_TAB_BG = "#DEAFEE"       # Active tab background (light lavender)
ACTIVE_TAB_FG = "#111"            # Active tab text (near-black)
