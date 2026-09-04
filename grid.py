"""Converting between screen pixels and grid tiles.

The floor plan is measured in tiles, the mouse is measured in pixels, and
this module is the only place where the two meet.  Keeping the conversion
here means the drawing code and the rules code never have to think about it.

Levels are different sizes, so the tile size is worked out each time from
how much room is available on screen.
"""

from constants import GRID_AREA_RECT, GRID_PADDING
from rules import wall_key


def tile_size(floor_plan):
    """Return the size in pixels of one grid tile for this floor plan.

    Bigger floor plans get smaller tiles so that every level fits the same
    area on screen.  The tile is square, so we take whichever of the two
    directions is tighter.
    """
    area_x, area_y, area_width, area_height = GRID_AREA_RECT
    usable_width = area_width - 2 * GRID_PADDING
    usable_height = area_height - 2 * GRID_PADDING

    size_from_width = usable_width // floor_plan.width
    size_from_height = usable_height // floor_plan.height
    return max(1, min(size_from_width, size_from_height))


def grid_pixel_size(floor_plan):
    """Return the total (width, height) of the drawn grid, in pixels."""
    size = tile_size(floor_plan)
    return (floor_plan.width * size, floor_plan.height * size)


def grid_origin(floor_plan):
    """Return the screen pixel position of the grid's top-left corner.

    The grid is centred inside its area, so plans of different shapes all
    look deliberate rather than shoved into a corner.
    """
    area_x, area_y, area_width, area_height = GRID_AREA_RECT
    pixel_width, pixel_height = grid_pixel_size(floor_plan)
    origin_x = area_x + (area_width - pixel_width) // 2
    origin_y = area_y + (area_height - pixel_height) // 2
    return (origin_x, origin_y)


def grid_to_screen(floor_plan, grid_x, grid_y):
    """Return the screen pixel position of the top-left corner of a tile."""
    origin_x, origin_y = grid_origin(floor_plan)
    size = tile_size(floor_plan)
    return (origin_x + grid_x * size, origin_y + grid_y * size)


def screen_to_grid(floor_plan, screen_x, screen_y):
    """Return the grid tile the given pixel sits on.

    TODO 1
    This is the opposite of grid_to_screen() just above, and it is the single
    most important function in the file: it is how a mouse click becomes a
    tile.  Read grid_to_screen() first - you are undoing exactly what it does.

    Work out the two steps:
      1. How far is the pixel from the grid's top-left corner?
         grid_origin() gives you that corner.
      2. How many whole tiles fit into that distance?
         tile_size() gives you the size of one tile.  Use // so you get a
         whole number of tiles rather than a fraction.

    The result may be outside the floor plan when the mouse is beside the
    grid.  Do not clamp it here - clamp_to_plan() below does that job.

    Returns:
        A tuple (grid_x, grid_y) of whole numbers.

    Right now this always returns tile (0, 0), so every click lands in the
    top-left corner of the plan.  You will know it works when the green drag
    preview appears under your mouse and grows and shrinks as you drag,
    instead of being stuck in the corner.
    """
    return (0, 0)


def clamp_to_plan(floor_plan, grid_x, grid_y):
    """Pull a tile position back inside the floor plan if it strayed outside.

    This is what stops a drag that runs off the edge of the grid from
    creating a room outside the building.
    """
    clamped_x = max(0, min(floor_plan.width - 1, grid_x))
    clamped_y = max(0, min(floor_plan.height - 1, grid_y))
    return (clamped_x, clamped_y)


def is_inside_grid(floor_plan, grid_x, grid_y):
    """Return True when a tile position is inside the floor plan.

    TODO 2
    A tile is inside when its x is at least 0 and less than the plan's width,
    and its y is at least 0 and less than the plan's height.

    Watch the "less than": a plan 10 tiles wide has tiles 0 to 9, so tile 10
    is outside it.

    The game uses this to ignore clicks that land beside the grid.  Returning
    True for everything, as it does now, means clicks outside the building
    are treated as if they were inside it.
    """
    return True


def edge_at_screen_position(floor_plan, screen_x, screen_y):
    """Return the interior wall edge nearest to a pixel, or None.

    Walls sit between two tiles rather than on a tile, so the player is
    aiming at a line and not at a square.  We work out which tile the mouse
    is in, then how far it is across that tile in each direction, and pick
    whichever of the four sides is closest.

    Returns a wall_key(), or None when the nearest side is on the outside of
    the building — the outer walls are already there and cannot be drawn on.
    """
    origin_x, origin_y = grid_origin(floor_plan)
    size = tile_size(floor_plan)

    grid_x, grid_y = screen_to_grid(floor_plan, screen_x, screen_y)
    if not is_inside_grid(floor_plan, grid_x, grid_y):
        return None

    # How far across the tile the mouse is, from 0.0 to 1.0.
    across = (screen_x - origin_x) / size - grid_x
    down = (screen_y - origin_y) / size - grid_y

    # Distance to each of the four sides, and the neighbour beyond it.
    sides = [
        (across, (grid_x - 1, grid_y)),
        (1 - across, (grid_x + 1, grid_y)),
        (down, (grid_x, grid_y - 1)),
        (1 - down, (grid_x, grid_y + 1)),
    ]
    distance, neighbour = min(sides)

    if not is_inside_grid(floor_plan, neighbour[0], neighbour[1]):
        return None

    return wall_key((grid_x, grid_y), neighbour)


def rectangle_from_drag(start_tile, end_tile):
    """Turn the two ends of a mouse drag into (grid_x, grid_y, width, height).

    The player can drag in any direction, so the starting tile is not always
    the top-left one.  Dragging up and to the left would give a negative
    width, which draws nothing and breaks every overlap check, so we take the
    smaller coordinate as the corner and use abs() for the size.

    Both ends of the drag are included: pressing and releasing on the same
    tile makes a 1 x 1 room, not a 0 x 0 one.  That is where the + 1 comes from.
    """
    start_x, start_y = start_tile
    end_x, end_y = end_tile

    grid_x = min(start_x, end_x)
    grid_y = min(start_y, end_y)
    width = abs(end_x - start_x) + 1
    height = abs(end_y - start_y) + 1

    return (grid_x, grid_y, width, height)
