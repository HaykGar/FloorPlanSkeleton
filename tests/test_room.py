"""Tests for the Room class."""

from room import Room


def make_bedroom():
    """A 5 x 4 block of bedroom tiles with its corner at (2, 3)."""
    tiles = {(2 + column, 3 + row) for row in range(4) for column in range(5)}
    return Room("bedroom", tiles, 6000)

def test_area_is_the_number_of_tiles():
    room = make_bedroom()
    assert room.area() == 20


# -- TODO 22: write these ---------------------------------------------------
#
#   test_cost_is_area_times_cost_per_tile
#   test_a_one_tile_room_has_an_area_of_one
#   test_an_l_shaped_room_counts_only_the_tiles_it_has
#       (a room is a set of tiles, so an L counts 5, not the 9 of its
#        bounding box - this is the test that would catch someone going back
#        to width times height)
#   test_room_contains_its_own_corner_tile
#   test_room_contains_its_far_corner_tile
#       (make_bedroom() starts at (2, 3) and is 5 by 4, so its last tile is
#        (6, 6), not (7, 7))
#   test_room_does_not_contain_a_tile_just_past_its_edge
#   test_display_name_comes_from_the_room_type
