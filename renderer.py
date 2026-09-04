"""All of the drawing.

The renderer shows what other modules have already worked out.  It never
decides whether an area can be painted, what a design costs, or whether the
client is happy: it is handed those answers and puts them on the screen.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from constants import (
    BANNER_RECT,
    COLOR_ACCENT,
    COLOR_BACKGROUND,
    COLOR_BUTTON,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_HOVER,
    COLOR_FAIL,
    COLOR_GRID_BACKGROUND,
    COLOR_GRID_BORDER,
    COLOR_GRID_LINE,
    COLOR_PANEL,
    COLOR_PANEL_EDGE,
    COLOR_PASS,
    COLOR_PREVIEW_INVALID,
    COLOR_PREVIEW_VALID,
    COLOR_ROOM_DEFAULT,
    COLOR_SELECTION,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_WALL,
    COLOR_WARNING,
    GRID_AREA_RECT,
    RESULTS_PANEL_RECT,
    ROOM_TYPES,
    SIDEBAR_RECT,
    TOOLBAR_RECT,
    TOOL_ERASE,
    TOOL_WALL,
    WALL_THICKNESS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    Color,
    Edge,
    Point,
)
from floor_plan import FloorPlan
from grid import grid_origin, grid_to_screen, tile_size
from room import Room

if TYPE_CHECKING:
    # game.py imports this file, so importing it back at run time would be
    # a circular import.  This import only happens for the type hints.
    from game import Game


FONT_NAMES = "Helvetica Neue,Helvetica,Arial,DejaVu Sans"


def room_color(room: Room, level: dict | None) -> Color:
    """Return the fill colour for a room, honouring any level override."""
    overrides = level.get("room_colors", {}) if level else {}
    if room.room_type in overrides:
        return tuple(overrides[room.room_type])
    settings = ROOM_TYPES.get(room.room_type, {})
    return settings.get("color", COLOR_ROOM_DEFAULT)


def darken(color: Color, amount: int = 60) -> Color:
    """Return a darker version of a colour, used for borders and shadows."""
    return tuple(max(0, channel - amount) for channel in color[:3])


def lighten(color: Color, amount: int = 40) -> Color:
    """Return a lighter version of a colour."""
    return tuple(min(255, channel + amount) for channel in color[:3])


def format_money(amount: int) -> str:
    """Return a number as a readable price, for example $118,000."""
    return "${:,}".format(int(amount))


def room_outline_segments(room: Room, floor_plan: FloorPlan) -> list[tuple[Point, Point]]:
    """Return the pixel line segments that trace the edge of a room.

    A room can be any shape, so its outline is not a rectangle.  A tile's
    side is on the outline when the tile beyond it is not part of the same
    room.  Drawing only those sides traces the blob exactly, whatever shape
    the player painted.
    """
    size = tile_size(floor_plan)
    segments = []

    for tile in room.tiles:
        tile_x, tile_y = tile
        x, y = grid_to_screen(floor_plan, tile_x, tile_y)

        if (tile_x, tile_y - 1) not in room.tiles:
            segments.append(((x, y), (x + size, y)))
        if (tile_x, tile_y + 1) not in room.tiles:
            segments.append(((x, y + size), (x + size, y + size)))
        if (tile_x - 1, tile_y) not in room.tiles:
            segments.append(((x, y), (x, y + size)))
        if (tile_x + 1, tile_y) not in room.tiles:
            segments.append(((x + size, y), (x + size, y + size)))

    return segments


def wall_segment(floor_plan: FloorPlan, edge: Edge) -> tuple[Point, Point]:
    """Return the two pixel endpoints of the line for one interior wall."""
    tile_a, tile_b = edge
    size = tile_size(floor_plan)

    if tile_a[0] != tile_b[0]:
        # Side by side, so the wall between them is vertical.
        left_tile = tile_a if tile_a[0] < tile_b[0] else tile_b
        x, y = grid_to_screen(floor_plan, left_tile[0] + 1, left_tile[1])
        return ((x, y), (x, y + size))

    # One above the other, so the wall is horizontal.
    top_tile = tile_a if tile_a[1] < tile_b[1] else tile_b
    x, y = grid_to_screen(floor_plan, top_tile[0], top_tile[1] + 1)
    return ((x, y), (x + size, y))


class Renderer:
    """Owns the window and the fonts, and draws every screen."""

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        # Fonts are created once here.  Building a font every frame is one of
        # the easiest ways to make a Pygame program stutter.
        self.font_title = pygame.font.SysFont(FONT_NAMES, 30, bold=True)
        self.font_heading = pygame.font.SysFont(FONT_NAMES, 15, bold=True)
        self.font_body = pygame.font.SysFont(FONT_NAMES, 16)
        self.font_small = pygame.font.SysFont(FONT_NAMES, 13)
        self.font_room = pygame.font.SysFont(FONT_NAMES, 14, bold=True)
        self.font_tiny = pygame.font.SysFont(FONT_NAMES, 11)

    # -- small drawing helpers ---------------------------------------------

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Color,
        x: int,
        y: int,
        align: str = "left",
    ) -> pygame.Rect:
        """Draw one line of text and return the rectangle it filled."""
        surface = font.render(str(text), True, color)
        rect = surface.get_rect()
        if align == "left":
            rect.topleft = (x, y)
        elif align == "center":
            rect.midtop = (x, y)
        else:
            rect.topright = (x, y)
        self.screen.blit(surface, rect)
        return rect

    def draw_wrapped_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Color,
        x: int,
        y: int,
        max_width: int,
        line_height: int = 18,
    ) -> int:
        """Draw text broken across several lines so it fits max_width pixels."""
        words = str(text).split()
        line = ""
        current_y = y
        for word in words:
            candidate = word if line == "" else line + " " + word
            if font.size(candidate)[0] <= max_width:
                line = candidate
            else:
                self.draw_text(line, font, color, x, current_y)
                current_y += line_height
                line = word
        if line:
            self.draw_text(line, font, color, x, current_y)
            current_y += line_height
        return current_y

    def font_that_fits(self, text: str, max_width: int) -> pygame.font.Font:
        """Return the largest of our body fonts that fits text into max_width.

        Level files are written by hand, so a long client requirement should
        shrink rather than spill out of the sidebar.
        """
        for font in [self.font_small, self.font_tiny]:
            if font.size(str(text))[0] <= max_width:
                return font
        return self.font_tiny

    def draw_panel(
        self,
        rect: pygame.Rect | tuple[int, int, int, int],
        color: Color = COLOR_PANEL,
        edge: Color = COLOR_PANEL_EDGE,
        radius: int = 10,
    ) -> None:
        """Draw one of the rounded background panels."""
        pygame.draw.rect(self.screen, color, rect, border_radius=radius)
        pygame.draw.rect(self.screen, edge, rect, width=1, border_radius=radius)

    def draw_button(
        self,
        button: dict,
        mouse_position: Point,
        is_active: bool = False,
        enabled: bool = True,
        font: pygame.font.Font | None = None,
    ) -> None:
        """Draw a button dictionary: {"label": ..., "rect": ..., "action": ...}."""
        rect = button["rect"]
        hovered = enabled and rect.collidepoint(mouse_position)
        font = font or self.font_body

        if not enabled:
            fill = COLOR_PANEL
            text_color = COLOR_TEXT_DIM
        elif is_active:
            fill = COLOR_BUTTON_ACTIVE
            text_color = (16, 20, 30)
        elif hovered:
            fill = COLOR_BUTTON_HOVER
            text_color = COLOR_TEXT
        else:
            fill = COLOR_BUTTON
            text_color = COLOR_TEXT

        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PANEL_EDGE, rect, width=1, border_radius=8)
        label_y = rect.y + (rect.height - font.get_height()) // 2
        self.draw_text(button["label"], font, text_color, rect.centerx, label_y, "center")

    def draw_translucent_rect(self, rect: pygame.Rect, color: Color, alpha: int) -> None:
        """Draw a see-through rectangle, used for drag previews."""
        surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        surface.fill((color[0], color[1], color[2], alpha))
        self.screen.blit(surface, (rect.x, rect.y))

    # -- level select screen -----------------------------------------------

    def draw_level_select(
        self,
        levels: list[dict],
        buttons: list[dict],
        mouse_position: Point,
        error_messages: list[str],
    ) -> None:
        """Draw the screen where the player picks a client brief."""
        self.screen.fill(COLOR_BACKGROUND)

        self.draw_text(
            "Floor Plan Challenge", self.font_title, COLOR_TEXT, WINDOW_WIDTH // 2, 84, "center"
        )
        self.draw_text(
            "Choose a client",
            self.font_body,
            COLOR_TEXT_DIM,
            WINDOW_WIDTH // 2,
            124,
            "center",
        )

        for index, button in enumerate(buttons):
            rect = button["rect"]
            hovered = rect.collidepoint(mouse_position)
            edge = COLOR_ACCENT if hovered else COLOR_PANEL_EDGE
            self.draw_panel(rect, COLOR_PANEL, edge, radius=12)

            # A level file is hand-written data, so every field is read with
            # .get() and a fallback.  A half-finished or damaged level should
            # look wrong on screen, not crash the program.
            level = levels[index]
            self.draw_text(
                level.get("name", "Unnamed level"),
                self.font_title,
                COLOR_TEXT,
                rect.x + 24,
                rect.y + 20,
            )
            bottom = self.draw_wrapped_text(
                level.get("client_brief", ""),
                self.font_body,
                COLOR_TEXT_DIM,
                rect.x + 24,
                rect.y + 62,
                rect.width - 48,
            )
            details = "{} x {} tiles      Budget {}      {} requirements".format(
                level.get("plan_width", "?"),
                level.get("plan_height", "?"),
                format_money(level.get("budget", 0)),
                len(level.get("requirements", [])),
            )
            self.draw_text(details, self.font_small, COLOR_ACCENT, rect.x + 24, bottom + 8)

        if error_messages:
            y = WINDOW_HEIGHT - 30 - 18 * len(error_messages)
            for message in error_messages:
                self.draw_text("Level file problem: " + message, self.font_small, COLOR_FAIL, 24, y)
                y += 18

    # -- design screen -----------------------------------------------------

    def draw_design(self, game: Game) -> None:
        """Draw the main design studio."""
        self.screen.fill(COLOR_BACKGROUND)
        self.draw_banner(game.level)
        self.draw_grid_area(game)
        self.draw_sidebar(game)
        self.draw_toolbar(game)
        self.draw_message(game)

    def draw_banner(self, level: dict) -> None:
        self.draw_panel(BANNER_RECT, COLOR_PANEL, COLOR_PANEL_EDGE, radius=0)
        self.draw_text("CLIENT", self.font_tiny, COLOR_ACCENT, 20, 12)
        self.draw_text(level.get("name", "Unnamed level"), self.font_heading, COLOR_TEXT, 20, 26)
        self.draw_text(
            level.get("client_brief", ""),
            self.font_small,
            COLOR_TEXT_DIM,
            WINDOW_WIDTH - 20,
            26,
            "right",
        )

    def draw_grid_area(self, game: Game) -> None:
        self.draw_panel(GRID_AREA_RECT, COLOR_GRID_BACKGROUND, COLOR_PANEL_EDGE)

        floor_plan = game.floor_plan
        size = tile_size(floor_plan)
        origin_x, origin_y = grid_origin(floor_plan)
        plan_width_pixels = floor_plan.width * size
        plan_height_pixels = floor_plan.height * size

        # The building outline.
        outline = pygame.Rect(origin_x, origin_y, plan_width_pixels, plan_height_pixels)
        pygame.draw.rect(self.screen, (26, 29, 37), outline)

        for column in range(floor_plan.width + 1):
            x = origin_x + column * size
            pygame.draw.line(
                self.screen, COLOR_GRID_LINE, (x, origin_y), (x, origin_y + plan_height_pixels)
            )
        for row in range(floor_plan.height + 1):
            y = origin_y + row * size
            pygame.draw.line(
                self.screen, COLOR_GRID_LINE, (origin_x, y), (origin_x + plan_width_pixels, y)
            )

        pygame.draw.rect(self.screen, COLOR_GRID_BORDER, outline, width=2)

        rooms = floor_plan.rooms()
        selected = game.selected_room()

        for room in rooms:
            self.draw_room(room, floor_plan, game.level)

        if selected is not None:
            for start, end in room_outline_segments(selected, floor_plan):
                pygame.draw.line(self.screen, COLOR_SELECTION, start, end, 3)

        # Interior walls go on top of the rooms, because that is what they do
        # in the design: they cut across a painted area.
        for edge in floor_plan.walls:
            start, end = wall_segment(floor_plan, edge)
            pygame.draw.line(self.screen, COLOR_WALL, start, end, WALL_THICKNESS)

        if game.selected_tool == TOOL_WALL and game.hovered_edge is not None:
            start, end = wall_segment(floor_plan, game.hovered_edge)
            pygame.draw.line(self.screen, COLOR_ACCENT, start, end, WALL_THICKNESS)
        elif game.drag_rectangle is not None:
            self.draw_preview(game)

    def draw_room(self, room: Room, floor_plan: FloorPlan, level: dict | None) -> None:
        """Draw one room: its tiles, its outline, and its label."""
        size = tile_size(floor_plan)
        color = room_color(room, level)

        for tile in room.tiles:
            x, y = grid_to_screen(floor_plan, tile[0], tile[1])
            pygame.draw.rect(self.screen, color, (x, y, size, size))

        for start, end in room_outline_segments(room, floor_plan):
            pygame.draw.line(self.screen, darken(color, 70), start, end, 2)

        self.draw_room_label(room, floor_plan, color, size)

    def draw_room_label(self, room: Room, floor_plan: FloorPlan, color: Color, size: int) -> None:
        """Draw the room's name and area, if the room is big enough to hold it."""
        label = room.display_name()
        if room.area() < 4 or self.font_room.size(label)[0] > size * 3:
            return

        label_x, label_y = room.label_tile()
        x, y = grid_to_screen(floor_plan, label_x, label_y)
        center_x = x + size // 2
        center_y = y + size // 2

        self.draw_text(
            label, self.font_room, darken(color, 110), center_x, center_y - 14, "center"
        )
        self.draw_text(
            "{} tiles".format(room.area()),
            self.font_tiny,
            darken(color, 80),
            center_x,
            center_y + 2,
            "center",
        )

    def draw_preview(self, game: Game) -> None:
        """Draw the area the player is currently dragging out."""
        grid_x, grid_y, width, height = game.drag_rectangle
        floor_plan = game.floor_plan
        size = tile_size(floor_plan)
        x, y = grid_to_screen(floor_plan, grid_x, grid_y)
        rect = pygame.Rect(x, y, width * size, height * size)

        erasing = game.selected_tool == TOOL_ERASE
        if erasing:
            color = COLOR_WARNING
        else:
            color = COLOR_PREVIEW_VALID if game.drag_is_valid else COLOR_PREVIEW_INVALID

        self.draw_translucent_rect(rect, color, 90)
        pygame.draw.rect(self.screen, color, rect, width=2)

        area = width * height
        if erasing:
            label = "{} x {}  =  erase {} tiles".format(width, height, area)
        else:
            cost = area * game.selected_cost_per_tile()
            label = "{} x {}  =  {} tiles   {}".format(width, height, area, format_money(cost))
        self.draw_text(label, self.font_small, COLOR_TEXT, rect.centerx, rect.y - 18, "center")

    def draw_sidebar(self, game: Game) -> None:
        self.draw_panel(SIDEBAR_RECT, COLOR_PANEL, COLOR_PANEL_EDGE)
        sidebar_x = SIDEBAR_RECT[0] + 16
        inner_width = SIDEBAR_RECT[2] - 32
        mouse_position = pygame.mouse.get_pos()

        self.draw_text("ROOM TYPES", self.font_tiny, COLOR_ACCENT, sidebar_x, 92)
        for button in game.palette_buttons:
            is_active = button["tool"] == game.selected_tool
            self.draw_palette_button(button, mouse_position, is_active, game.level)

        self.draw_text("TOOLS", self.font_tiny, COLOR_ACCENT, sidebar_x, 308)
        for button in game.tool_buttons:
            is_active = button["tool"] == game.selected_tool
            self.draw_button(button, mouse_position, is_active=is_active, font=self.font_small)

        self.draw_selected_room_box(game, sidebar_x, 374, inner_width)
        self.draw_budget_box(game, sidebar_x, 440, inner_width)

        self.draw_text("REQUIREMENTS", self.font_tiny, COLOR_ACCENT, sidebar_x, 512)
        text_x = sidebar_x + 42
        text_width = SIDEBAR_RECT[0] + SIDEBAR_RECT[2] - 16 - text_x
        y = 534
        for result in game.requirement_results:
            symbol = "PASS" if result["passed"] else "FAIL"
            color = COLOR_PASS if result["passed"] else COLOR_FAIL
            self.draw_text(symbol, self.font_tiny, color, sidebar_x, y + 2)
            font = self.font_that_fits(result["description"], text_width)
            self.draw_text(result["description"], font, COLOR_TEXT, text_x, y)
            y += 21

    def draw_palette_button(
        self, button: dict, mouse_position: Point, is_active: bool, level: dict | None
    ) -> None:
        """Draw one room-type button, including its colour swatch and price."""
        rect = button["rect"]
        hovered = rect.collidepoint(mouse_position)
        fill = COLOR_BUTTON_HOVER if (hovered or is_active) else COLOR_BUTTON
        edge = COLOR_ACCENT if is_active else COLOR_PANEL_EDGE

        pygame.draw.rect(self.screen, fill, rect, border_radius=8)
        pygame.draw.rect(self.screen, edge, rect, width=2 if is_active else 1, border_radius=8)

        settings = ROOM_TYPES[button["tool"]]
        overrides = level.get("room_colors", {}) if level else {}
        swatch_color = tuple(overrides.get(button["tool"], settings["color"]))
        swatch = pygame.Rect(rect.x + 10, rect.y + 10, 20, 20)
        pygame.draw.rect(self.screen, swatch_color, swatch, border_radius=4)

        self.draw_text(settings["display_name"], self.font_body, COLOR_TEXT, rect.x + 42, rect.y + 6)
        self.draw_text(
            format_money(settings["cost_per_tile"]) + " / tile",
            self.font_tiny,
            COLOR_TEXT_DIM,
            rect.x + 42,
            rect.y + 24,
        )

    def draw_selected_room_box(self, game: Game, x: int, y: int, width: int) -> None:
        self.draw_text("SELECTED ROOM", self.font_tiny, COLOR_ACCENT, x, y)
        room = game.selected_room()
        if room is None:
            self.draw_text("Click a room to select it", self.font_small, COLOR_TEXT_DIM, x, y + 18)
            return
        self.draw_text(room.display_name(), self.font_body, COLOR_TEXT, x, y + 16)
        self.draw_text(
            "{} tiles".format(room.area()), self.font_small, COLOR_TEXT_DIM, x, y + 36
        )
        self.draw_text(format_money(room.cost()), self.font_small, COLOR_WARNING, x + width, y + 36, "right")

    def draw_budget_box(self, game: Game, x: int, y: int, width: int) -> None:
        total_cost = game.floor_plan.total_cost()
        budget = game.level.get("budget", 0)
        over_budget = total_cost > budget

        self.draw_text("BUDGET", self.font_tiny, COLOR_ACCENT, x, y)
        self.draw_text(format_money(total_cost), self.font_heading, COLOR_TEXT, x, y + 16)
        self.draw_text(
            "of " + format_money(budget), self.font_small, COLOR_TEXT_DIM, x + width, y + 18, "right"
        )

        # The bar fills up as the design gets more expensive.
        bar = pygame.Rect(x, y + 40, width, 10)
        pygame.draw.rect(self.screen, (24, 26, 33), bar, border_radius=5)
        if budget > 0:
            fraction = min(1.0, total_cost / budget)
            filled_width = int(width * fraction)
            if filled_width > 0:
                filled = pygame.Rect(x, y + 40, filled_width, 10)
                color = COLOR_FAIL if over_budget else COLOR_PASS
                pygame.draw.rect(self.screen, color, filled, border_radius=5)

        if over_budget:
            self.draw_text(
                "Over budget by " + format_money(total_cost - budget),
                self.font_tiny,
                COLOR_FAIL,
                x,
                y + 54,
            )

    def draw_toolbar(self, game: Game) -> None:
        self.draw_panel(TOOLBAR_RECT, COLOR_PANEL, COLOR_PANEL_EDGE, radius=0)
        mouse_position = pygame.mouse.get_pos()
        for button in game.toolbar_buttons:
            enabled = True
            if button["action"] == "delete":
                enabled = game.selected_room() is not None
            self.draw_button(button, mouse_position, enabled=enabled)

    def draw_message(self, game: Game) -> None:
        """Draw the short status message that appears after an action."""
        if not game.message or game.message_frames_left <= 0:
            return

        area_x, area_y, area_width, area_height = GRID_AREA_RECT
        text_surface = self.font_body.render(game.message, True, COLOR_TEXT)
        padding = 14
        box = pygame.Rect(
            0, 0, text_surface.get_width() + padding * 2, text_surface.get_height() + padding
        )
        box.centerx = area_x + area_width // 2
        box.bottom = area_y + area_height - 14

        # Fade the toast out over its last half second.
        alpha = min(230, int(230 * game.message_frames_left / 30))
        background = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
        color = COLOR_FAIL if game.message_is_error else (54, 60, 76)
        background.fill((color[0], color[1], color[2], alpha))
        self.screen.blit(background, box.topleft)
        self.screen.blit(text_surface, (box.x + padding, box.y + padding // 2))

    # -- results screen ----------------------------------------------------

    def draw_results(self, game: Game) -> None:
        """Draw the design screen with the score summary on top of it."""
        self.draw_design(game)

        shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        shade.fill((10, 12, 16, 200))
        self.screen.blit(shade, (0, 0))

        panel = pygame.Rect(RESULTS_PANEL_RECT)
        self.draw_panel(panel, COLOR_PANEL, COLOR_ACCENT, radius=14)

        score = game.score_result
        headline = "Client approved!" if score["passed_all"] else "Client has notes"
        headline_color = COLOR_PASS if score["passed_all"] else COLOR_WARNING
        self.draw_text(headline, self.font_title, headline_color, panel.centerx, panel.y + 28, "center")

        self.draw_text(
            str(score["score"]) + " points",
            self.font_title,
            COLOR_TEXT,
            panel.centerx,
            panel.y + 74,
            "center",
        )

        rows = [
            (
                "Requirements met  ({} of {})".format(
                    score["requirements_passed"], score["requirements_total"]
                ),
                score["requirement_points"],
            ),
            ("Money left over", score["budget_bonus"]),
            ("Space used well", score["space_bonus"]),
        ]
        y = panel.y + 140
        for label, points in rows:
            self.draw_text(label, self.font_body, COLOR_TEXT_DIM, panel.x + 40, y)
            self.draw_text(
                "+" + str(points), self.font_body, COLOR_TEXT, panel.right - 40, y, "right"
            )
            y += 28

        y += 12
        for result in score["results"]:
            color = COLOR_PASS if result["passed"] else COLOR_FAIL
            symbol = "PASS" if result["passed"] else "FAIL"
            self.draw_text(symbol, self.font_tiny, color, panel.x + 40, y + 2)
            self.draw_text(result["description"], self.font_small, COLOR_TEXT, panel.x + 82, y)
            y += 20

        mouse_position = pygame.mouse.get_pos()
        for button in game.results_buttons:
            self.draw_button(button, mouse_position)
