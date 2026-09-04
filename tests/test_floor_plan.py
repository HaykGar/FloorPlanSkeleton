"""Tests for the FloorPlan class."""

from floor_plan import FloorPlan
from rules import wall_key


def make_plan() -> FloorPlan:
    return FloorPlan(12, 10)

def test_painting_over_another_room_type_is_refused():
    plan = make_plan()
    plan.paint((1, 1, 4, 3), "bedroom")

    assert plan.paint((2, 2, 3, 3), "kitchen") is False
    # Nothing may have changed, not even partly.
    assert len(plan.rooms()) == 1
    assert plan.rooms()[0].room_type == "bedroom"


# -- TODO 22: write these ---------------------------------------------------
#
# Painting
#   test_a_new_floor_plan_is_empty
#   test_a_valid_area_can_be_painted
#   test_painting_over_the_same_room_type_is_allowed
#       (this is what lets a player grow and touch up a room, so it must NOT
#        be refused)
#   test_painting_outside_the_boundary_is_refused
#   test_painting_an_area_with_no_size_is_refused
#   test_paint_error_explains_why_an_area_was_refused
#       (check the message mentions another room, not just that it is not
#        None)
#   test_room_at_position_finds_the_room_covering_a_tile
#   test_room_at_position_returns_none_on_an_empty_tile
#
# Erasing
#   test_erasing_clears_tiles_and_reports_how_many
#   test_erasing_empty_space_clears_nothing
#   test_erasing_can_split_a_room_in_two
#       (erase the middle tile of a row and you should get two rooms)
#   test_erasing_a_room_removes_all_of_it
#
# Walls - wall_key() from rules.py names the wall between two tiles
#   test_a_wall_can_be_added_and_removed
#   test_adding_the_same_wall_twice_changes_nothing
#   test_removing_a_wall_that_was_never_there_changes_nothing
#   test_walls_split_a_painted_area_into_two_rooms
#
# Remembering rooms
#   test_the_room_list_is_recalculated_after_every_change
#       (paint, check the area, paint again, check it changed.  This is the
#        test that catches a missing design_changed() call)
#   test_total_cost_updates_as_the_design_changes
#   test_clearing_removes_everything
