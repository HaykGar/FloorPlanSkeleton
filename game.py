"""The Game class: it wires everything together and runs the main loop.

The Game decides *when* things happen.  It asks other modules to work out
*what* the answer is: rules.py judges the design, floor_plan.py guards the
grid, storage.py touches files, and renderer.py draws.
"""

import pygame

import rules
import storage
from constants import (
    DEFAULT_SAVE_FILE,
    FRAMES_PER_SECOND,
    GRID_AREA_RECT,
    LEVEL_FILES,
    MESSAGE_FRAMES,
    RESULTS_PANEL_RECT,
    ROOM_TYPES,
    ROOM_TYPE_ORDER,
    SIDEBAR_RECT,
    STATE_DESIGNING,
    STATE_LEVEL_SELECT,
    STATE_RESULTS,
    TOOL_ERASE,
    TOOL_WALL,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from floor_plan import FloorPlan
from grid import (
    clamp_to_plan,
    edge_at_screen_position,
    is_inside_grid,
    rectangle_from_drag,
    screen_to_grid,
)
from renderer import Renderer


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.running = True

        self.levels, self.level_errors = storage.load_all_levels(LEVEL_FILES)

        self.state = STATE_LEVEL_SELECT
        self.level = None
        self.floor_plan = FloorPlan(1, 1)

        # The tool the player is holding: a room type name, TOOL_ERASE, or
        # TOOL_WALL.
        self.selected_tool = ROOM_TYPE_ORDER[0]

        # Selection is remembered as a tile rather than as a room object,
        # because rooms are worked out fresh from the grid every time it
        # changes.  A room object from one moment would be a stale copy the
        # next.
        self.selected_tile = None

        # Painting drag.
        self.drag_start_tile = None
        self.drag_rectangle = None
        self.drag_is_valid = False

        # Wall drag.  wall_drag_adds is decided by the first edge touched:
        # starting on empty space draws walls, starting on a wall rubs them
        # out, so one tool does both without a separate eraser.
        self.wall_drag_active = False
        self.wall_drag_adds = True
        self.hovered_edge = None

        self.requirement_results = []
        self.score_result = None

        self.message = ""
        self.message_frames_left = 0
        self.message_is_error = False

        self.level_buttons = build_level_buttons(len(self.levels))
        self.palette_buttons = build_palette_buttons()
        self.tool_buttons = build_tool_buttons()
        self.toolbar_buttons = build_toolbar_buttons()
        self.results_buttons = build_results_buttons()

    # -- main loop ---------------------------------------------------------

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            self.clock.tick(FRAMES_PER_SECOND)
        pygame.quit()

    def update(self):
        if self.message_frames_left > 0:
            self.message_frames_left -= 1

    def draw(self):
        if self.state == STATE_LEVEL_SELECT:
            self.renderer.draw_level_select(
                self.levels, self.level_buttons, pygame.mouse.get_pos(), self.level_errors
            )
        elif self.state == STATE_DESIGNING:
            self.renderer.draw_design(self)
        else:
            self.renderer.draw_results(self)
        pygame.display.flip()

    # -- events ------------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return

        if self.state == STATE_LEVEL_SELECT:
            self.handle_level_select_event(event)
        elif self.state == STATE_DESIGNING:
            self.handle_designing_event(event)
        else:
            self.handle_results_event(event)

    def handle_level_select_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, button in enumerate(self.level_buttons):
                if button["rect"].collidepoint(event.pos):
                    self.start_level(self.levels[index])

    def handle_designing_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.handle_mouse_up(event.pos)
        elif event.type == pygame.KEYDOWN:
            self.handle_key_down(event.key)

    def handle_results_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for button in self.results_buttons:
                if button["rect"].collidepoint(event.pos):
                    if button["action"] == "keep_designing":
                        self.state = STATE_DESIGNING
                    else:
                        self.state = STATE_LEVEL_SELECT
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = STATE_DESIGNING

    # -- mouse -------------------------------------------------------------

    def handle_mouse_down(self, position):
        for button in self.palette_buttons + self.tool_buttons:
            if button["rect"].collidepoint(position):
                self.selected_tool = button["tool"]
                return

        for button in self.toolbar_buttons:
            if button["rect"].collidepoint(position):
                self.do_action(button["action"])
                return

        if not point_is_in_rect(position, GRID_AREA_RECT):
            return

        if self.selected_tool == TOOL_WALL:
            self.start_wall_drag(position)
            return

        grid_x, grid_y = screen_to_grid(self.floor_plan, position[0], position[1])
        if not is_inside_grid(self.floor_plan, grid_x, grid_y):
            return

        self.selected_tile = (grid_x, grid_y)
        self.drag_start_tile = (grid_x, grid_y)
        self.update_drag((grid_x, grid_y))

    def handle_mouse_motion(self, position):
        if self.selected_tool == TOOL_WALL:
            self.hovered_edge = edge_at_screen_position(
                self.floor_plan, position[0], position[1]
            )
            if self.wall_drag_active:
                self.apply_wall_at(position)
            return

        self.hovered_edge = None
        if self.drag_start_tile is None:
            return

        grid_x, grid_y = screen_to_grid(self.floor_plan, position[0], position[1])
        # The mouse is allowed to leave the grid mid-drag; the area just stops
        # growing at the wall instead of the drag being cancelled.
        end_tile = clamp_to_plan(self.floor_plan, grid_x, grid_y)
        self.update_drag(end_tile)

    def handle_mouse_up(self, position):
        if self.wall_drag_active:
            self.wall_drag_active = False
            self.refresh_requirements()
            return

        if self.drag_start_tile is None:
            return

        rectangle = self.drag_rectangle
        self.drag_start_tile = None
        self.drag_rectangle = None

        if rectangle is None:
            return

        if self.selected_tool == TOOL_ERASE:
            cleared = self.floor_plan.erase(rectangle)
            if cleared == 0:
                self.set_message("Nothing to erase there.", is_error=True)
            self.selected_tile = None
            self.refresh_requirements()
            return

        problem = self.floor_plan.paint_error(rectangle, self.selected_tool)
        if problem is not None:
            self.set_message(problem, is_error=True)
            return

        self.floor_plan.paint(rectangle, self.selected_tool)
        self.refresh_requirements()

    def update_drag(self, end_tile):
        """Work out the area the player is currently dragging out."""
        self.drag_rectangle = rectangle_from_drag(self.drag_start_tile, end_tile)
        if self.selected_tool == TOOL_ERASE:
            self.drag_is_valid = True
        else:
            self.drag_is_valid = self.floor_plan.can_paint(
                self.drag_rectangle, self.selected_tool
            )

    # -- walls -------------------------------------------------------------

    def start_wall_drag(self, position):
        edge = edge_at_screen_position(self.floor_plan, position[0], position[1])
        if edge is None:
            return
        # The first edge decides whether this drag is drawing or rubbing out.
        self.wall_drag_adds = not self.floor_plan.has_wall(edge)
        self.wall_drag_active = True
        self.apply_wall_at(position)

    def apply_wall_at(self, position):
        edge = edge_at_screen_position(self.floor_plan, position[0], position[1])
        if edge is None:
            return
        if self.wall_drag_adds:
            self.floor_plan.add_wall(edge)
        else:
            self.floor_plan.remove_wall(edge)

    # -- selection ---------------------------------------------------------

    def selected_room(self):
        """Return the room the player has selected, or None.

        Worked out from the selected tile each time it is asked for, so it is
        never a stale copy of a room that has since been repainted.
        """
        if self.selected_tile is None:
            return None
        return self.floor_plan.room_at_position(self.selected_tile[0], self.selected_tile[1])

    def selected_cost_per_tile(self):
        """Return the price per tile of the held tool, or 0 for a non-room tool."""
        settings = ROOM_TYPES.get(self.selected_tool)
        if settings is None:
            return 0
        return settings["cost_per_tile"]

    # -- keyboard ----------------------------------------------------------

    def handle_key_down(self, key):
        if key in (pygame.K_DELETE, pygame.K_BACKSPACE):
            self.do_action("delete")
        elif key == pygame.K_e:
            self.selected_tool = TOOL_ERASE
        elif key == pygame.K_w:
            self.selected_tool = TOOL_WALL
        elif key == pygame.K_s:
            self.do_action("save")
        elif key == pygame.K_l:
            self.do_action("load")
        elif key == pygame.K_RETURN:
            self.do_action("check")
        elif key == pygame.K_ESCAPE:
            self.do_action("levels")
        else:
            # Number keys 1 to 4 pick a room type.
            number_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
            if key in number_keys:
                index = number_keys.index(key)
                if index < len(ROOM_TYPE_ORDER):
                    self.selected_tool = ROOM_TYPE_ORDER[index]

    # -- actions -----------------------------------------------------------

    def do_action(self, action):
        if action == "delete":
            self.delete_selected_room()
        elif action == "save":
            self.save_design()
        elif action == "load":
            self.load_design()
        elif action == "clear":
            self.floor_plan.clear()
            self.selected_tile = None
            self.refresh_requirements()
            self.set_message("Floor plan cleared.")
        elif action == "check":
            self.check_design()
        elif action == "levels":
            self.state = STATE_LEVEL_SELECT

    def delete_selected_room(self):
        room = self.selected_room()
        if room is None:
            self.set_message("Select a room first.", is_error=True)
            return
        name = room.display_name()
        self.floor_plan.erase_room(room)
        self.selected_tile = None
        self.refresh_requirements()
        self.set_message("Deleted the " + name + ".")

    def save_design(self):
        try:
            storage.save_design(
                DEFAULT_SAVE_FILE, self.floor_plan, self.level.get("level_id", "unknown")
            )
        except ValueError as error:
            self.set_message(str(error), is_error=True)
            return
        self.set_message("Design saved to " + DEFAULT_SAVE_FILE + ".")

    def load_design(self):
        try:
            design = storage.load_design(DEFAULT_SAVE_FILE)
        except ValueError as error:
            self.set_message(str(error), is_error=True)
            return

        if design["level"] != self.level.get("level_id", "unknown"):
            self.set_message("That design was made for a different level.", is_error=True)
            return

        # Anything outside the building outline is dropped rather than
        # trusted, in case the file was edited by hand.
        self.floor_plan.clear()
        dropped = 0
        for tile, room_type in design["tiles"].items():
            if is_inside_grid(self.floor_plan, tile[0], tile[1]):
                self.floor_plan.tiles[tile] = room_type
            else:
                dropped += 1
        self.floor_plan.walls = design["walls"]
        self.floor_plan.remove_stranded_walls()
        self.floor_plan.design_changed()

        self.selected_tile = None
        self.refresh_requirements()
        if dropped > 0:
            self.set_message(
                "Loaded, but " + str(dropped) + " tile(s) were outside the building.",
                is_error=True,
            )
        else:
            self.set_message("Design loaded.")

    def check_design(self):
        self.score_result = rules.calculate_score(self.floor_plan, self.level)
        self.state = STATE_RESULTS

    # -- level handling ----------------------------------------------------

    def start_level(self, level):
        self.level = level
        # .get() with a fallback so a half-written level file gives a small
        # empty grid rather than a crash on the way into the design screen.
        self.floor_plan = FloorPlan(level.get("plan_width", 10), level.get("plan_height", 8))
        self.selected_tile = None
        self.selected_tool = ROOM_TYPE_ORDER[0]
        self.drag_start_tile = None
        self.drag_rectangle = None
        self.wall_drag_active = False
        self.hovered_edge = None
        self.score_result = None
        self.state = STATE_DESIGNING
        self.refresh_requirements()
        self.message = ""
        self.message_frames_left = 0

    def refresh_requirements(self):
        """Recalculate the requirement list after the design changed.

        This runs once per change rather than once per frame: the answer only
        moves when the grid does.
        """
        self.requirement_results = rules.check_requirements(self.floor_plan, self.level)

    def set_message(self, text, is_error=False):
        self.message = text
        self.message_is_error = is_error
        self.message_frames_left = MESSAGE_FRAMES


# ---------------------------------------------------------------------------
# Button layouts
#
# A button is a plain dictionary.  The renderer draws it and the game checks
# whether it was clicked, so both sides agree on one simple shape.
# ---------------------------------------------------------------------------


def point_is_in_rect(point, rect):
    x, y, width, height = rect
    return x <= point[0] < x + width and y <= point[1] < y + height


def build_level_buttons(level_count):
    buttons = []
    for index in range(level_count):
        rect = pygame.Rect(150, 180 + index * 164, 800, 140)
        buttons.append({"label": "level", "rect": rect, "action": "start_level"})
    return buttons


def build_palette_buttons():
    buttons = []
    x = SIDEBAR_RECT[0] + 16
    width = SIDEBAR_RECT[2] - 32
    for index, room_type in enumerate(ROOM_TYPE_ORDER):
        rect = pygame.Rect(x, 112 + index * 46, width, 40)
        buttons.append(
            {
                "label": ROOM_TYPES[room_type]["display_name"],
                "rect": rect,
                "action": "select_tool",
                "tool": room_type,
            }
        )
    return buttons


def build_tool_buttons():
    x = SIDEBAR_RECT[0] + 16
    width = (SIDEBAR_RECT[2] - 32 - 8) // 2
    return [
        {
            "label": "Erase",
            "rect": pygame.Rect(x, 326, width, 34),
            "action": "select_tool",
            "tool": TOOL_ERASE,
        },
        {
            "label": "Wall",
            "rect": pygame.Rect(x + width + 8, 326, width, 34),
            "action": "select_tool",
            "tool": TOOL_WALL,
        },
    ]


def build_toolbar_buttons():
    labels_and_actions = [
        ("Delete", "delete"),
        ("Save", "save"),
        ("Load", "load"),
        ("Clear", "clear"),
        ("Check Design", "check"),
        ("Levels", "levels"),
    ]
    buttons = []
    for index, (label, action) in enumerate(labels_and_actions):
        rect = pygame.Rect(20 + index * 150, 722, 140, 40)
        buttons.append({"label": label, "rect": rect, "action": action})
    return buttons


def build_results_buttons():
    panel_x, panel_y, panel_width, panel_height = RESULTS_PANEL_RECT
    button_y = panel_y + panel_height - 56
    center_x = panel_x + panel_width // 2
    return [
        {
            "label": "Keep Designing",
            "rect": pygame.Rect(center_x - 210, button_y, 200, 40),
            "action": "keep_designing",
        },
        {
            "label": "Choose Level",
            "rect": pygame.Rect(center_x + 10, button_y, 200, 40),
            "action": "choose_level",
        },
    ]
