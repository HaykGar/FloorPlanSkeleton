"""Tests for finding rooms, the geometry rules, and scoring."""

from constants import Tile
from floor_plan import FloorPlan
from room import Room
from rules import (
    calculate_score,
    calculate_total_cost,
    check_requirements,
    find_rooms,
    minimum_area_for,
    neighbours,
    rectangle_is_inside_plan,
    rooms_are_adjacent,
    tiles_in_rectangle,
    wall_key,
)


def block(room_type: str, grid_x: int, grid_y: int, width: int, height: int) -> dict[Tile, str]:
    """Build a {tile: room_type} dictionary for a rectangle of tiles."""
    return {
        (grid_x + column, grid_y + row): room_type
        for row in range(height)
        for column in range(width)
    }


# -- tiles and walls --------------------------------------------------------

def test_touching_tiles_of_the_same_type_are_one_room():
    # This is the whole point of the model: painting a bedroom beside an
    # existing bedroom grows it instead of making a second one.
    tiles = block("bedroom", 0, 0, 3, 3)
    tiles.update(block("bedroom", 3, 0, 1, 1))

    rooms = find_rooms(tiles, set())

    assert len(rooms) == 1
    assert rooms[0].area() == 10

def test_rooms_touching_only_at_a_corner_are_not_adjacent():
    # These two meet at the single point (4, 4).  A door cannot go there.
    kitchen = Room("kitchen", tiles_in_rectangle((0, 0, 4, 4)), 100)
    living = Room("living_room", tiles_in_rectangle((4, 4, 3, 3)), 100)
    assert rooms_are_adjacent(kitchen, living) is False

def make_level(requirements: list[dict], budget: int = 1000000) -> dict:
    return {
        "level_id": "test_level",
        "name": "Test Level",
        "client_brief": "",
        "plan_width": 12,
        "plan_height": 10,
        "budget": budget,
        "minimum_areas": {},
        "requirements": requirements,
    }


# Run the tests now, before you write anything.  The corner test above
# already passes and the merging test fails.
#
# That is not because adjacency is secretly finished.  It is because
# rooms_are_adjacent() returns False until you write it, and a test asking
# "is this False?" is happy with a function that says False about everything.
#
# A test that passes for the wrong reason is worse than no test, because it
# tells you something works when it does not.  That is why the list below
# always pairs a False case with a True case.  Whenever you write a test that
# passes straight away, stop and ask whether it could be passing by accident.


# -- TODO 22: write these ---------------------------------------------------
#
# Tiles and walls
#   test_a_tile_has_four_neighbours
#   test_a_diagonal_tile_is_not_a_neighbour
#   test_a_wall_has_the_same_name_whichever_way_round_it_is_given
#       (otherwise the same wall could be stored twice, and rubbing it out
#        once would leave half of it behind)
#
# Finding rooms - use block() above to build a {tile: room_type} dictionary
#   test_an_empty_grid_has_no_rooms
#   test_touching_tiles_of_different_types_are_separate_rooms
#   test_tiles_of_the_same_type_with_a_gap_are_separate_rooms
#   test_tiles_joined_only_at_a_corner_are_separate_rooms
#   test_an_l_shaped_blob_is_one_room
#   test_a_wall_splits_one_blob_into_two_rooms
#   test_a_wall_that_does_not_cut_all_the_way_through_leaves_one_room
#       (the tiles can still be reached by going around the end of the wall -
#        this is the one that catches a flood fill that gives up too early)
#
# Adjacency
#   test_rooms_sharing_a_vertical_wall_are_adjacent
#   test_rooms_sharing_a_horizontal_wall_are_adjacent
#   test_rooms_with_a_gap_between_them_are_not_adjacent
#   test_a_wall_between_two_rooms_does_not_stop_them_being_adjacent
#
# Boundaries
#   test_a_rectangle_that_fits_exactly_is_inside_the_plan
#   test_a_rectangle_hanging_over_the_right_edge_is_outside_the_plan
#   test_a_rectangle_with_a_negative_position_is_outside_the_plan
#   test_a_rectangle_with_no_size_is_never_inside_the_plan
#
# Cost
#   test_total_cost_adds_up_every_room
#   test_total_cost_of_an_empty_design_is_zero
#
# Minimum areas
#   test_a_level_can_raise_a_minimum_area
#   test_a_level_cannot_lower_a_minimum_area
#       (bedroom is 12 in constants.py, so a level asking for 5 changes
#        nothing)
#
# Requirements - use make_level() above with a FloorPlan
#   test_a_required_room_fails_when_it_is_missing
#   test_a_required_room_passes_once_it_is_painted
#   test_two_bedrooms_painted_touching_only_count_as_one
#   test_a_wall_turns_one_bedroom_into_the_two_the_client_asked_for
#   test_a_minimum_area_requirement_fails_when_one_room_is_too_small
#   test_a_not_adjacent_requirement_fails_when_the_rooms_touch
#   test_the_budget_requirement_fails_when_the_design_costs_too_much
#
# Scoring
#   test_going_over_budget_earns_no_budget_bonus
