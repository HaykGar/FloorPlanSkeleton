"""One room in the design.

A room is not a rectangle.  It is a connected blob of tiles that all have the
same room type — whatever shape the player painted.  Two bedrooms drawn next
to each other are one bedroom, exactly like a real floor plan, unless the
player draws a wall between them.

Rooms are *worked out* from the grid rather than stored.  See
rules.find_rooms().
"""

from typing import Any

from constants import ROOM_TYPES, COLOR_ROOM_DEFAULT, Color, Tile


class Room:
    """A connected group of same-type tiles."""

    def __init__(self, room_type: str, tiles: set[Tile], cost_per_tile: int) -> None:
        self.room_type = room_type
        # A set, because the order of the tiles never matters and "is this
        # tile in the room?" is asked constantly.
        self.tiles = set(tiles)
        self.cost_per_tile = cost_per_tile

    def area(self) -> int:
        """Return how many grid tiles this room covers.

        TODO 3
        A room is a set of tiles, so its area is just how many tiles are in
        that set.  Python has a built-in function that counts the things in
        a set.

        Returning 0 for now means every room reads as empty and free, and the
        rest of the program still runs.
        
        Hint: it's the same function you would use to get the LENgth of a list or string.  Do you remember what it is?
        Also, make sure you are using self.tiles instead of just tiles, which is a local variable that doesn't exist in this method.
        """

        # return amount of grid tiles the room covers

        return len(self.tiles)

    def cost(self) -> int:
        """Return the total cost of building this room.

        TODO 4
        Every tile of the room costs self.cost_per_tile dollars.

        Call the method you just wrote rather than counting the tiles a
        second time.  If area() is ever wrong, you want it to be wrong in
        exactly one place.
        
        Hint: to call functions that are part of the same class, you need to use self.  For example, self.area() will call the area() method of this Room object.
        """

        # this should give the total cost of building the room
        return self.area() * self.cost_per_tile

    def contains_grid_position(self, grid_x: int, grid_y: int) -> bool:
        """Return True when the tile (grid_x, grid_y) is part of this room.

        TODO 5
        This is what makes clicking a room select it.

        self.tiles is a set of (x, y) tuples.  Build the tuple for the tile
        you were given and ask whether it is in the set.  One line, and no
        loop is needed - checking whether something is in a set is the thing
        sets are fastest at.
        
        Hint: to build a tuple, you can use parentheses like this: (var1, var2).
        The "in" keyword is also useful here.
        """
        return (grid_x, grid_y) in self.tiles

    def bounding_box(self) -> tuple[int, int, int, int]:
        """Return (min_x, min_y, max_x, max_y) of the tiles in this room.

        Used only for drawing.  The room itself may be any shape inside it.
        """
        xs = [tile[0] for tile in self.tiles]
        ys = [tile[1] for tile in self.tiles]
        return (min(xs), min(ys), max(xs), max(ys))

    def label_tile(self) -> Tile:
        """Return a tile near the middle of the room, for drawing its name.

        The middle of an L-shaped room can fall outside the room, so we take
        the tile of the room that is closest to the average position.
        """
        average_x = sum(tile[0] for tile in self.tiles) / len(self.tiles)
        average_y = sum(tile[1] for tile in self.tiles) / len(self.tiles)
        return min(
            self.tiles,
            key=lambda tile: (tile[0] - average_x) ** 2 + (tile[1] - average_y) ** 2,
        )

    def display_name(self) -> str:
        """Return the human-readable name of this room's type."""
        return room_type_setting(self.room_type, "display_name", self.room_type)

    def color(self) -> Color:
        """Return the fill colour for this room."""
        return room_type_setting(self.room_type, "color", COLOR_ROOM_DEFAULT)


def room_type_setting(room_type: str, setting_name: str, fallback: Any) -> Any:
    """Look up one setting for a room type, or return fallback if it is missing.

    Saved files and level files are written by hand, so an unknown room type
    is always possible.  Returning a fallback keeps the game from crashing.
    """
    settings = ROOM_TYPES.get(room_type, {})
    return settings.get(setting_name, fallback)
