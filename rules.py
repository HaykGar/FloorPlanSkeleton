"""Every rule that decides whether a floor plan is any good.

Nothing in this file draws anything or reads the mouse.  These are plain
calculations, which is exactly why they are easy to test.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from constants import (
    MAX_BUDGET_BONUS,
    MAX_SPACE_BONUS,
    POINTS_PER_REQUIREMENT,
    ROOM_TYPES,
    Edge,
    Rectangle,
    Tile,
)
from room import Room, room_type_setting

if TYPE_CHECKING:
    # floor_plan.py imports this file, so importing it back at run time would
    # be a circular import.  This import only happens for the type hints.
    from floor_plan import FloorPlan


# ---------------------------------------------------------------------------
# Tiles, neighbours, and walls
# ---------------------------------------------------------------------------


def neighbours(tile: Tile) -> list[Tile]:
    """Return the four tiles that share a wall with this one.

    TODO 11
    A tile is a tuple (x, y).  Return a list of the four tiles directly left,
    right, above, and below it.

    Diagonal tiles are NOT neighbours.  Two tiles touching at a corner have
    no wall between them, so you could not put a door there.  Getting this
    wrong is what makes rooms leak diagonally into each other.

    Returns:
        A list of four (x, y) tuples.

    While this returns an empty list, no tile can reach any other, so every
    painted tile shows up as its own tiny room.
    """
    return []


def wall_key(tile_a: Tile, tile_b: Tile) -> Edge:
    """Return the standard way of naming the wall between two tiles.

    A wall sits between two tiles, and the pair (A, B) means the same wall as
    (B, A).  Storing them in a fixed order means one wall has exactly one
    name, so a set of walls never ends up holding the same wall twice.
    """
    return tuple(sorted([tuple(tile_a), tuple(tile_b)]))


def tiles_are_joined(
    tile_a: Tile, tile_b: Tile, tiles: dict[Tile, str], walls: set[Edge]
) -> bool:
    """Return True when two neighbouring tiles belong to the same room.

    Two tiles are joined when they are both painted, both painted with the
    same room type, and there is no wall drawn between them.

    TODO 12
    This one small function is what makes rooms behave the way they do:
    because it says yes, painting a bedroom beside an existing bedroom grows
    that bedroom instead of making a second one, and because a wall makes it
    say no, drawing a wall through a room splits it in two.

    Three things must all be true.  Check them in this order:
      1. Both tiles are actually painted.  'tiles' is a dictionary, and a
         tile that is not in it is empty floor.
      2. They are painted with the same room type.
      3. There is no wall between them.  wall_key() just above turns two
         tiles into the name of the wall between them; check whether that
         name is in 'walls'.

    Returns:
        True or False.
    """
    return False


def tiles_in_rectangle(rectangle: Rectangle) -> set[Tile]:
    """Return the set of tiles covered by (grid_x, grid_y, width, height)."""
    grid_x, grid_y, width, height = rectangle
    return {
        (grid_x + column, grid_y + row)
        for row in range(height)
        for column in range(width)
    }


def rectangle_is_inside_plan(rectangle: Rectangle, floor_plan: FloorPlan) -> bool:
    """Return True when every tile of the rectangle is inside the building.

    TODO 13
    A rectangle is a tuple (grid_x, grid_y, width, height).  Unpack it first.

    Five things can be wrong: the rectangle can have no size at all, or it
    can stick out past the left, the top, the right, or the bottom.

    Remember that floor_plan.width is a number of tiles, so a plan 10 wide
    has tiles 0 to 9.  A rectangle at x = 8 that is 3 wide does not fit.

    Returns:
        True or False.
    """
    return True


# ---------------------------------------------------------------------------
# Working out where the rooms are
# ---------------------------------------------------------------------------


def find_rooms(tiles: dict[Tile, str], walls: set[Edge]) -> list[Room]:
    """Work out the rooms in a design.

    'tiles' maps a tile to its room type.  'walls' is a set of wall_key()s.

    A room is a group of tiles that all have the same type and are joined to
    each other, where two neighbouring tiles count as joined unless there is
    a wall between them.  So painting a bedroom next to an existing bedroom
    grows that bedroom, and drawing a wall through the middle of one splits
    it into two.

    This is a flood fill.  Starting from a tile nobody has visited yet, keep
    a to-do list of tiles that belong to the same room, and repeatedly take
    one off, look at its four neighbours, and add any that also belong.  When
    the to-do list runs dry, that room is complete and we look for the next
    unvisited tile.

    Returns a list of Room objects, in a stable order so the display does not
    jump around between frames.
    """
    rooms = []
    visited = set()

    for start_tile in sorted(tiles):
        if start_tile in visited:
            continue

        room_type = tiles[start_tile]
        room_tiles = set()

        to_visit = [start_tile]
        visited.add(start_tile)

        while to_visit:
            tile = to_visit.pop()
            room_tiles.add(tile)

            for neighbour in neighbours(tile):
                if neighbour in visited:
                    continue
                if not tiles_are_joined(tile, neighbour, tiles, walls):
                    continue
                visited.add(neighbour)
                to_visit.append(neighbour)

        rooms.append(
            Room(room_type, room_tiles, room_type_setting(room_type, "cost_per_tile", 0))
        )

    return rooms


def rooms_are_adjacent(room1: Room, room2: Room) -> bool:
    """Return True when the two rooms share part of a wall.

    Any tile of one room neighbouring any tile of the other is enough.
    Rooms touching only at a corner are not adjacent, because corner tiles
    are not neighbours.

    A wall drawn between them does NOT stop them being adjacent — a wall
    between two rooms is exactly what "sharing a wall" means.  Walls only
    decide where one room ends and the next begins.  So this function never
    looks at walls at all.

    TODO 15
    Go through every tile of the first room, and for each one look at its
    neighbours().  If any of those neighbours is a tile of the second room,
    the two rooms touch, so return True straight away.  If you get all the
    way through without finding one, return False.

    Corner contact takes care of itself: a diagonal tile is not a neighbour,
    so you do not need a special case for it.

    Returns:
        True or False.
    """
    return False


# ---------------------------------------------------------------------------
# Money and space
# ---------------------------------------------------------------------------


def calculate_total_cost(rooms: list[Room]) -> int:
    """Return the combined cost of every room in the list.

    TODO 14
    Add up the cost() of every room.  An empty list must give 0, not an
    error.

    sum() with a comprehension does this in one line, but a loop building up
    a running total is just as correct.  The budget bar and the under-budget
    requirement both read this, so they stay at zero until it works.
    """
    return 0


def calculate_used_tiles(rooms: list[Room]) -> int:
    """Return how many grid tiles are covered by rooms."""
    return sum(room.area() for room in rooms)


def minimum_area_for(room_type: str, level: dict) -> int:
    """Return the smallest allowed area for a room type on this level.

    Each room type has a sensible default in constants.py.  A level may
    demand something larger, but it can never make a room type smaller.
    """
    type_settings = ROOM_TYPES.get(room_type, {})
    default_minimum = type_settings.get("minimum_area", 1)
    level_minimums = level.get("minimum_areas", {})
    level_minimum = level_minimums.get(room_type, 0)
    return max(default_minimum, level_minimum)


def rooms_of_type(rooms: list[Room], room_type: str) -> list[Room]:
    """Return only the rooms that have the given type."""
    return [room for room in rooms if room.room_type == room_type]


# ---------------------------------------------------------------------------
# Client requirements
# ---------------------------------------------------------------------------


def any_pair_is_adjacent(rooms_a: list[Room], rooms_b: list[Room]) -> bool:
    """Return True when at least one room from each list shares a wall."""
    for room_a in rooms_a:
        for room_b in rooms_b:
            if rooms_are_adjacent(room_a, room_b):
                return True
    return False


def check_one_requirement(requirement: dict, floor_plan: FloorPlan, level: dict) -> bool:
    """Return True when this single client requirement is satisfied."""
    kind = requirement.get("kind")
    rooms = floor_plan.rooms()

    if kind == "required_room":
        return len(rooms_of_type(rooms, requirement["room_type"])) >= 1

    if kind == "under_budget":
        return floor_plan.total_cost() <= level["budget"]

    # TODO 16
    # Add the other four requirement kinds here, each as its own
    # `if kind == ...:` block, following the two worked examples above.
    #
    #   "room_count"    keys: room_type, count
    #                   At least 'count' rooms of that type exist.
    #                   rooms_of_type() gives you the matching rooms.
    #
    #   "minimum_area"  keys: room_type
    #                   EVERY room of that type is at least
    #                   minimum_area_for(room_type, level) tiles.
    #                   A design with no rooms of that type does NOT satisfy
    #                   it — decide what to do about that before you write
    #                   the loop.
    #
    #   "adjacent"      keys: room_type_a, room_type_b
    #                   At least one room of each type shares a wall.
    #                   any_pair_is_adjacent() does the work.
    #
    #   "not_adjacent"  keys: room_type_a, room_type_b
    #                   NO room of one type shares a wall with the other.
    #                   This is the exact opposite of "adjacent".
    #
    # Add them one at a time and watch one more line of the requirement panel
    # come alive each time.

    # An unknown requirement kind can never be satisfied, but it must not
    # crash the game either.  The level file is simply wrong.
    return False


def check_requirements(floor_plan: FloorPlan, level: dict) -> list[dict]:
    """Check every requirement of the level.

    Returns a list of dictionaries, one per requirement:

        {"description": "Include a kitchen", "passed": True}

    The renderer turns this list into PASS and FAIL labels.  It does not
    decide anything itself.
    """
    results = []
    for requirement in level.get("requirements", []):
        results.append(
            {
                "description": describe_requirement(requirement),
                "passed": check_one_requirement(requirement, floor_plan, level),
            }
        )
    return results


def describe_requirement(requirement: dict) -> str:
    """Return the text shown to the player for one requirement."""
    if "description" in requirement:
        return requirement["description"]
    # Fallback so a level file without descriptions still shows something.
    return str(requirement.get("kind", "unknown requirement"))


def count_passed(results: list[dict]) -> int:
    """Return how many requirement results passed."""
    return sum(1 for result in results if result["passed"])


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def calculate_score(floor_plan: FloorPlan, level: dict) -> dict:
    """Score a finished design and explain where the points came from.

    The formula has three parts:

      1. Requirements  100 points for each client requirement satisfied.
      2. Budget bonus  up to 200 points for money left over.  A design that
                       spends the whole budget earns 0, one that spends half
                       earns 100.  Going over budget earns nothing.
      3. Space bonus   up to 200 points for filling the building outline.
                       Covering every tile earns the full 200.

    Returns a dictionary so the results screen can show the breakdown.
    """
    results = check_requirements(floor_plan, level)
    passed = count_passed(results)

    requirement_points = passed * POINTS_PER_REQUIREMENT

    budget = level.get("budget", 0)
    total_cost = floor_plan.total_cost()
    if budget > 0 and total_cost <= budget:
        money_left_fraction = (budget - total_cost) / budget
        budget_bonus = int(MAX_BUDGET_BONUS * money_left_fraction)
    else:
        budget_bonus = 0

    total_tiles = floor_plan.width * floor_plan.height
    if total_tiles > 0:
        used_fraction = calculate_used_tiles(floor_plan.rooms()) / total_tiles
        space_bonus = int(MAX_SPACE_BONUS * used_fraction)
    else:
        space_bonus = 0

    return {
        "requirement_points": requirement_points,
        "budget_bonus": budget_bonus,
        "space_bonus": space_bonus,
        "score": requirement_points + budget_bonus + space_bonus,
        "requirements_passed": passed,
        "requirements_total": len(results),
        "passed_all": passed == len(results) and len(results) > 0,
        "results": results,
    }
