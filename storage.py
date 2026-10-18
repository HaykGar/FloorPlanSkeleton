"""Reading and writing files.

Every open(), every json call, and every file-related try/except in the
project lives here.  If a file is missing or damaged, these functions raise
ValueError with a message that is safe to show the player.
"""

import json
import os
from typing import Any

from constants import LEVELS_FOLDER, ROOM_TYPES, Edge, Tile
from floor_plan import FloorPlan
from rules import wall_key


PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def level_path(file_name: str) -> str:
    """Return the full path to a level file.

    Building the path from this file's own location means the game runs the
    same way no matter which folder you start it from.
    """
    return os.path.join(PROJECT_FOLDER, LEVELS_FOLDER, file_name)


def design_path(file_name: str) -> str:
    """Return the full path to a saved design file."""
    return os.path.join(PROJECT_FOLDER, file_name)


def read_json_file(path: str, what_it_is: str) -> Any:
    """Read one JSON file and return the data inside it.

    'what_it_is' is a word like "level" or "saved design", used to build the
    error message.

    TODO 17
    Open the file with `with open(path, "r") as file:` and return
    `json.load(file)`.

    Then catch the three things that realistically go wrong, each in its own
    `except` block, and raise a ValueError with a sentence a player could
    understand.  Put the path in the message — "file not found" is much
    less useful than knowing which file.

        FileNotFoundError       the file is not there
        json.JSONDecodeError    the file exists but is not valid JSON
        OSError                 anything else about reading it failed

    Catch them in that order.  FileNotFoundError is a kind of OSError, so a
    bare `except OSError` first would swallow it and you would lose the more
    helpful message.

    Do not write a bare `except:` — it hides real bugs in your own code.

    Everything that reads a file goes through here, so nothing loads until
    this works.
    """
    try:
        with open(path, 'r') as file:
            return json.load(file)
        
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e: 
        raise ValueError(f"Error: loading file {path} \n {e}")
        

    return {}


# ---------------------------------------------------------------------------
# Levels
# ---------------------------------------------------------------------------

REQUIRED_LEVEL_KEYS = [
    "level_id",
    "name",
    "client_brief",
    "plan_width",
    "plan_height",
    "budget",
    "requirements",
]


def load_level(file_name: str) -> dict:
    """Load one level file and check that it makes sense.

    Returns the level as a dictionary.  Raises ValueError with a readable
    message when the file is missing, damaged, or incomplete.

    TODO 18
    Steps:
      1. Build the full path with level_path().
      2. Read it with read_json_file(path, "level").  You do not need a
         try/except here — read_json_file already raises ValueError, and
         letting it travel up to the Game is the whole point of raising.
      3. Check the data really describes a level, raising ValueError with a
         clear message when it does not.  Level files are written by hand,
         so all of these happen:
           - the file holds a list, or a number, instead of an object
           - one of REQUIRED_LEVEL_KEYS above is missing 
           - plan_width or plan_height is less than 1
           - budget is negative
           - "requirements" is not a list
      4. Return the level dictionary.

    Checking here rather than in the Game means a typo in a level file gives
    a clear message instead of a crash twenty lines later.

    Until you write it, this returns the stand-in level below so that you
    still have a grid to paint on and a few requirements to work against.
    All three levels will look identical and carry the same practice brief,
    which is how you will know you are looking at the stand-in rather than at
    the real file.
    """

    path = level_path(file_name)

    level = read_json_file(path, "level")

    if not isinstance(level, dict):
        raise ValueError(f"Level is of type {type(level)}")

    for key in REQUIRED_LEVEL_KEYS:
        if key not in level:
            raise ValueError(f"missing key {key}")

    if level["plan_width"] < 1:
        raise ValueError("plan_width must be at least 1")
    
    if level["plan_height"] < 1:
        raise ValueError("plan_height must be at least 1")

    if level["budget"] < 0:
        raise ValueError("negative budget")

    if not isinstance(level["requirements"], list):
        raise ValueError(f"Requirement is of type {type(level["requirements"])}") 

    return level


def load_all_levels(file_names: list[str]) -> tuple[list[dict], list[str]]:
    """Load several levels, skipping any that are broken.

    Returns (levels, error_messages) so the game can still start with the
    levels that did work while telling the player about the ones that did not.
    """
    levels = []
    error_messages = []
    for file_name in file_names:
        try:
            levels.append(load_level(file_name))
        except ValueError as error:
            error_messages.append(str(error))
    return levels, error_messages


# ---------------------------------------------------------------------------
# Saved designs
#
# A design is saved as the grid itself — the painted tiles and the walls —
# not as a list of rooms.  Rooms are worked out from the grid when it loads,
# so a saved design cannot disagree with itself about where the rooms are.
# ---------------------------------------------------------------------------


def save_design(file_name: str, floor_plan: FloorPlan, level_id: str) -> str:
    """Write the current design to a JSON file.

    Raises ValueError when the file cannot be written.

    TODO 20
    Build a dictionary shaped exactly like this, because load_design() and
    the two *_from_data() functions read it back:

        {
            "level": "compact_apartment",
            "tiles": [
                {"x": 2, "y": 3, "room_type": "bedroom"}
            ],
            "walls": [
                {"x1": 2, "y1": 3, "x2": 3, "y2": 3}
            ]
        }

    floor_plan.tiles is a dictionary of tile -> room type, so
    `for tile, room_type in sorted(floor_plan.tiles.items())` walks it in a
    steady order.  floor_plan.walls is a set of pairs of tiles, so each edge
    is ((x1, y1), (x2, y2)).  Sorting both is not required, but it makes the
    saved file readable and stops it shuffling on every save.

    Write it with `with open(path, "w") as file:` and
    `json.dump(data, file, indent=4)`.  The indent is not decoration — it
    means you can open the save file and read it while debugging.

    Wrap the writing in try/except OSError and raise ValueError with a
    readable message.

    Returns:
        The path written to, so the game can tell the player where it went.
    """

    tiles_list = []
    for (x, y), room_types in sorted(floor_plan.tiles.items()):
        tiles_list.append({
            "x" : x,
            "y" : y,
            'room_type' : room_types
        })

    walls_list = []
    for (i1, i2) in sorted(floor_plan.walls):
        x1, y1 = i1
        x2, y2 = i2
        walls_list.append({
            "x1" : x1,
            "y1" : y1,
            'x2' : x2,
            'y2' : y2
        })

    data = {
        'level' : level_id,
        'tiles' : tiles_list,
        "walls" : walls_list
    }

    try: 
        with open(file_name, "w") as file:
            json.dump(data, file, indent=4)
    except OSError:
        raise ValueError(f"Couldnt save dsign to {file_name}")



    return design_path(file_name)


def whole_number(data: dict, key: str, what_it_is: str) -> int:
    """Return data[key], checking that it is a whole number."""
    if key not in data:
        raise ValueError("A saved " + what_it_is + " is missing '" + key + "'.")
    value = data[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("A saved " + what_it_is + " has a non-whole-number '" + key + "'.")
    return value


def tiles_from_data(tile_list: list) -> dict[Tile, str]:
    """Turn the saved tile list back into a {tile: room_type} dictionary.

    TODO 19
    walls_from_data() just below is the worked example — read it first, then
    write this one the same way.

    For every entry in the list:
      - refuse anything that is not a dictionary
      - refuse a "room_type" that is not a key of ROOM_TYPES (imported at the
        top).  A save file naming a room type you deleted must not crash the
        game three screens later.
      - read "x" and "y" with whole_number(entry, "x", "tile"), which does
        the missing-key and wrong-type checking for you
      - put them in the dictionary as tiles[(x, y)] = room_type

    Returns:
        A dictionary mapping (x, y) tuples to room type names.
    """

    tiles = {}

    for entry in tile_list:
        if not isinstance(entry, dict):
            raise ValueError("Tile entry has to be a dictionary!")

        room_type = entry.get("room_type")
        if room_type not in ROOM_TYPES:
            raise ValueError(f"This isnt a valid room type.. oops: {room_type}")

        x = whole_number(entry, "x", "tile")
        y = whole_number(entry, "y", "tile")

        tiles[(x, y)] = room_type

    return {}


def walls_from_data(wall_list: list) -> set[Edge]:
    """Turn the saved wall list back into a set of wall keys."""
    walls = set()
    for entry in wall_list:
        if not isinstance(entry, dict):
            raise ValueError("The saved design contains a wall that is not an object.")

        tile_a = (whole_number(entry, "x1", "wall"), whole_number(entry, "y1", "wall"))
        tile_b = (whole_number(entry, "x2", "wall"), whole_number(entry, "y2", "wall"))

        # A wall only means anything between two tiles that touch.
        steps_apart = abs(tile_a[0] - tile_b[0]) + abs(tile_a[1] - tile_b[1])
        if steps_apart != 1:
            raise ValueError("A saved wall is not between two neighbouring tiles.")

        walls.add(wall_key(tile_a, tile_b))
    return walls


def load_design(file_name: str) -> dict:
    """Read a saved design back from a JSON file.

    Returns {"level": level_id, "tiles": {...}, "walls": {...}}.
    Note that "tiles" comes back as a dictionary and "walls" as a set, ready
    to drop straight into a FloorPlan.
    Raises ValueError when anything about the file is wrong.

    TODO 21
    Steps:
      1. design_path(), then read_json_file(path, "saved design").
      2. Refuse anything that is not a dictionary, refuse it when any of
         "level", "tiles" or "walls" is missing, and refuse it when "tiles"
         or "walls" is not a list.
      3. Hand the two lists to tiles_from_data() and walls_from_data().  They
         raise their own ValueErrors with good messages, so you do not repeat
         their checks here.
      4. Return the three-key dictionary described above.

    Returning empty collections, as it does now, means Load appears to work
    but always gives you a blank plan.
    """
    return {"level": "", "tiles": {}, "walls": set()}
