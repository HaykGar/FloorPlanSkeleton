"""The design the player is building: a building outline, painted tiles, and
the interior walls the player has drawn.

The grid is what the program stores.  Rooms are not stored at all — they are
worked out from the grid whenever they are needed, by rules.find_rooms().
That is what makes two bedrooms painted next to each other become one
bedroom: there was never a "bedroom object" to keep them apart.
"""

from constants import Edge, Rectangle, Tile
from room import Room
from rules import (
    calculate_total_cost,
    find_rooms,
    rectangle_is_inside_plan,
    tiles_in_rectangle,
)

# Please do the TODOs in order, because later ones depend on earlier ones. Please start withTODO 6.

class FloorPlan:
    """Owns the painted tiles and the interior walls.

    Other modules should go through paint(), erase(), and toggle_wall()
    rather than reaching into self.tiles, so that the cached room list is
    thrown away whenever the design changes.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        # Maps a tile (x, y) to the name of the room type painted on it.
        # A tile that is not in the dictionary is empty floor.
        self.tiles: dict[Tile, str] = {}
        # A set of wall_key()s: the interior walls the player has drawn.
        self.walls: set[Edge] = set()
        # Worked out on demand, and thrown away whenever the design changes.
        self.cached_rooms: list[Room] | None = None

    # -- rooms -------------------------------------------------------------

    def rooms(self) -> list[Room]:
        """Return the list of rooms in the design.

        The flood fill is only worth doing when something has actually
        changed, so the answer is remembered until the next edit.  The
        renderer asks for the rooms sixty times a second.
        """
        if self.cached_rooms is None:
            self.cached_rooms = find_rooms(self.tiles, self.walls)
        return self.cached_rooms

    def design_changed(self) -> None:
        """Throw away the remembered room list.

        Every method that edits tiles or walls must call this.  Forgetting to
        is exactly the kind of bug that makes the screen show stale rooms.
        """
        self.cached_rooms = None

    def room_at_position(self, grid_x: int, grid_y: int) -> Room | None:
        """Return the room covering the given tile, or None if it is empty.

        TODO 9
        This is how clicking on a room selects it.

        Loop over self.rooms() -- which returns a list -- and ask each element whether it contains the tile,
        using the method you wrote in TODO 5 (in room.py).  Return the first room that does.  
        Return None when the tile is empty floor (ie there is no room at that tile).
        
        Hint: to check whether a tile is in a room, you can use the "in" keyword.
        """

        #loop thru each room in plan
        for room in self.rooms():
            #check if the room covers the mouse position
            if room.contains_grid_position(grid_x, grid_y):
                return room

        # if no room covers this spot return none
        return None

    # -- painting ----------------------------------------------------------

    def paint_error(self, rectangle: Rectangle, room_type: str) -> str | None:
        """Return a message explaining why an area cannot be painted.

        Returns None when the area is fine.  Returning the reason rather than
        just True or False is what lets the game tell the player why.

        TODO 6
        The message you return is shown on screen, so write it for a player to read.

        Two things to check, in this order:

          1. The whole rectangle must be inside the building. To check that, call 
             rectangle_is_inside_plan(rectangle, self).  It returns True when the 
             rectangle is inside the plan, and False when it is not.  If it is not, 
             return a message like "That area is outside the building."
             rectangle_is_inside_plan(rectangle, self) is imported for you.
             It still says yes to everything until you write TODO 13, so you
             will not see this check say no yet - the game already stops your
             drag at the edge of the grid.  Write the call anyway.
          2. No tile in the rectangle may already belong to a DIFFERENT room
             type.  tiles_in_rectangle(rectangle) gives you every tile to
             look at, and self.tiles.get(tile) gives you what is painted
             there, or None when it is empty floor.

             Painting over the same type must stay allowed — that is what
             lets a player touch up and grow a room.

        While this returns None for everything, any area can be painted
        anywhere, including straight over another room.
        
        Hint: to check whether a tile is in the rectangle, you can use the "in" keyword.  
        For example, if tile is a Tile object and rectangle is a Rectangle object, you can 
        write "if tile in rectangle:" to check if the tile is inside the rectangle.
        """

        # check if the rectangle falls outside the building plan
        if not rectangle_is_inside_plan(rectangle, self):
            return "That area is outside the building."

        # Check each tile to make sure it doesn't overlap 
        for tile in tiles_in_rectangle(rectangle):
            existing_room_type = self.tiles.get(tile)
            if existing_room_type is not None and existing_room_type != room_type:
                 return "That area is already part of another room."

        return None

    def can_paint(self, rectangle: Rectangle, room_type: str) -> bool:
        """Return True when the area may be painted."""
        return self.paint_error(rectangle, room_type) is None

    def paint(self, rectangle: Rectangle, room_type: str) -> bool:
        """Paint an area with a room type if it is allowed.

        Painting next to an existing room of the same type joins them into
        one room.  Painting over tiles that are already that type is
        harmless, which is what makes touching up a shape feel natural.

        Returns True when the area was painted, False when it was refused.

        TODO 7
        Use can_paint() rather than repeating the checks you just wrote.

        When it is allowed, set every tile of tiles_in_rectangle(rectangle)
        in self.tiles to room_type, then call self.design_changed() so the
        remembered room list is thrown away.  Forgetting that last line is
        the classic bug here: everything looks right until the screen keeps
        showing the old rooms.
        """

        # see if the paintings allowed
        if not self.can_paint(rectangle, room_type):
            return False

        for tile in tiles_in_rectangle(rectangle):
            self.tiles[tile] = room_type

        self.design_changed()
        return True

    def erase(self, rectangle: Rectangle) -> int:
        """Clear every tile in an area.

        Returns how many tiles were actually cleared.

        TODO 8
        Go through tiles_in_rectangle(rectangle) and delete each one that is
        in self.tiles, counting as you go.  Tiles that were already empty are
        not an error; they just do not count.

        If you cleared anything, call self.remove_stranded_walls() and then
        self.design_changed() before returning.
        
        Hint: to delete a key from a dictionary, you can use the "del" keyword. 
        For example, "del self.tiles[tile]" will remove the tile from the dictionary.

        Returns:
            The number of tiles cleared, as a whole number.
        """
        tiles_cleared = 0

        # loop thru tiles and delte them from self tiles if they exist
        for tile in tiles_in_rectangle(rectangle):
            if tile in self.tiles:
                del self.tiles[tile]
                tiles_cleared += 1

        # fix up issues if anythin was cleared
        if tiles_cleared > 0:
            self.remove_stranded_walls()
            self.design_changed()

        return tiles_cleared

    def erase_room(self, room: Room) -> None:
        """Clear every tile of one room."""
        for tile in room.tiles:
            if tile in self.tiles:
                del self.tiles[tile]
        self.remove_stranded_walls()
        self.design_changed()

    # -- walls -------------------------------------------------------------

    def has_wall(self, edge: Edge) -> bool:
        """Return True when a wall has been drawn on this edge."""
        return edge in self.walls

    def add_wall(self, edge: Edge) -> bool:
        """Draw a wall on an edge.  Returns True when something changed."""
        if edge in self.walls:
            return False
        self.walls.add(edge)
        self.design_changed()
        return True

    def remove_wall(self, edge: Edge) -> bool:
        """Rub out a wall.  Returns True when something changed."""
        if edge not in self.walls:
            return False
        self.walls.remove(edge)
        self.design_changed()
        return True

    def remove_stranded_walls(self) -> None:
        """Forget walls that no longer have a painted tile on either side.

        Without this, erasing a room would leave its interior walls behind,
        floating in empty space and quietly splitting whatever gets painted
        there next.
        """
        still_useful = set()
        for edge in self.walls:
            tile_a, tile_b = edge
            if tile_a in self.tiles or tile_b in self.tiles:
                still_useful.add(edge)

        if still_useful != self.walls:
            self.walls = still_useful
            self.design_changed()

    # -- money -------------------------------------------------------------

    def total_cost(self) -> int:
        """Return the combined cost of every room in the design.

        TODO 10
        One line.  rules.calculate_total_cost() already knows how, it is
        imported at the top of this file, and self.rooms() gives it the list
        it wants.

        The budget bar will still read $0 after you write this, because
        calculate_total_cost(...) will be fixed later.
        
        Hint: function definition looks like: def calculate_total_cost(rooms: list[Room])
        Do we have a list of rooms we can get by calling self.some_function()?
        """

        return calculate_total_cost(self.rooms())

    def clear(self) -> None:
        """Remove every tile and every wall."""
        self.tiles = {}
        self.walls = set()
        self.design_changed()
