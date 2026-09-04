"""Shared configuration values for the Floor Plan Challenge.

Everything in this file is data: sizes, colours, and room-type settings.
No game rules and no drawing code belong here.
"""

# ---------------------------------------------------------------------------
# Window
# ---------------------------------------------------------------------------

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 780
WINDOW_TITLE = "Floor Plan Challenge"
FRAMES_PER_SECOND = 60

# ---------------------------------------------------------------------------
# Layout
#
# The screen is divided into four areas.  Each one is (x, y, width, height).
# ---------------------------------------------------------------------------

BANNER_RECT = (0, 0, WINDOW_WIDTH, 60)
GRID_AREA_RECT = (20, 76, 736, 612)
SIDEBAR_RECT = (772, 76, 308, 612)
TOOLBAR_RECT = (0, 704, WINDOW_WIDTH, 76)

# The grid never draws right up against the edge of its area.
GRID_PADDING = 12

# The score summary panel, shared by the renderer and the button layout so
# the two can never drift apart.
RESULTS_PANEL_RECT = (290, 155, 520, 470)

# How many frames a status message stays on screen (60 frames = 1 second).
MESSAGE_FRAMES = 150

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

COLOR_BACKGROUND = (24, 26, 33)
COLOR_PANEL = (34, 37, 47)
COLOR_PANEL_EDGE = (52, 56, 70)
COLOR_GRID_BACKGROUND = (30, 33, 42)
COLOR_GRID_LINE = (48, 52, 65)
COLOR_GRID_BORDER = (96, 104, 128)

COLOR_TEXT = (228, 232, 242)
COLOR_TEXT_DIM = (138, 146, 168)
COLOR_ACCENT = (94, 169, 255)
COLOR_PASS = (86, 199, 133)
COLOR_FAIL = (232, 102, 102)
COLOR_WARNING = (235, 178, 84)

COLOR_BUTTON = (48, 52, 66)
COLOR_BUTTON_HOVER = (64, 70, 88)
COLOR_BUTTON_ACTIVE = (94, 169, 255)

COLOR_PREVIEW_VALID = (120, 220, 160)
COLOR_PREVIEW_INVALID = (232, 102, 102)
COLOR_SELECTION = (255, 224, 130)

COLOR_ROOM_DEFAULT = (255, 255, 255)

# Interior walls are drawn dark and thick so they read clearly on top of a
# room's fill colour.
COLOR_WALL = (16, 18, 24)
WALL_THICKNESS = 5

# ---------------------------------------------------------------------------
# Room types
#
# This dictionary describes the *kinds* of room that exist in the game.
# A Room object is one actual room in the player's design.
#
#   cost_per_tile  dollars charged for each grid tile the room covers
#   minimum_area   the smallest sensible size for this kind of room.
#                  A level may raise this value, but never lower it.
#   color          fill colour on the floor plan.  A level may override it.
# ---------------------------------------------------------------------------

ROOM_TYPES = {
    "bedroom": {
        "display_name": "Bedroom",
        "cost_per_tile": 6000,
        "minimum_area": 12,
        "color": (122, 152, 214),
    },
    "bathroom": {
        "display_name": "Bathroom",
        "cost_per_tile": 11000,
        "minimum_area": 4,
        "color": (108, 190, 201),
    },
    "kitchen": {
        "display_name": "Kitchen",
        "cost_per_tile": 9000,
        "minimum_area": 8,
        "color": (222, 158, 96),
    },
    "living_room": {
        "display_name": "Living Room",
        "cost_per_tile": 5000,
        "minimum_area": 16,
        "color": (168, 140, 206),
    },
}

# The order the room types appear in the palette.
ROOM_TYPE_ORDER = ["bedroom", "bathroom", "kitchen", "living_room"]

# ---------------------------------------------------------------------------
# Tools
#
# The player is always holding exactly one tool.  It is either the name of a
# room type (paint that kind of room) or one of these two.
# ---------------------------------------------------------------------------

TOOL_ERASE = "erase"
TOOL_WALL = "wall"

# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------

LEVELS_FOLDER = "levels"

LEVEL_FILES = [
    "compact_apartment.json",
    "family_home.json",
    "community_center.json",
]

DEFAULT_SAVE_FILE = "my_design.json"

# ---------------------------------------------------------------------------
# Scoring
#
# The full formula lives in rules.calculate_score().  These are its weights.
# ---------------------------------------------------------------------------

POINTS_PER_REQUIREMENT = 100
MAX_BUDGET_BONUS = 200
MAX_SPACE_BONUS = 200

# ---------------------------------------------------------------------------
# Game states
# ---------------------------------------------------------------------------

STATE_LEVEL_SELECT = "level_select"
STATE_DESIGNING = "designing"
STATE_RESULTS = "results"
