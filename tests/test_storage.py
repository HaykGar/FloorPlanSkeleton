"""Tests for reading and writing files.

These tests create real files and then delete them again, so running them
never leaves rubbish behind in the project folder.
"""

import os
from collections.abc import Callable

import storage
from floor_plan import FloorPlan
from rules import wall_key


TEMPORARY_FILE = "test_temporary_design.json"


def remove_temporary_file() -> None:
    path = storage.design_path(TEMPORARY_FILE)
    if os.path.exists(path):
        os.remove(path)

def write_temporary_file(text: str) -> None:
    with open(storage.design_path(TEMPORARY_FILE), "w") as file:
        file.write(text)

def expect_value_error(function: Callable[[], object], must_contain: str = "") -> None:
    """Run a function that should raise ValueError, and check its message."""
    try:
        function()
        assert False, "Expected a ValueError"
    except ValueError as error:
        assert must_contain in str(error), str(error)


# -- levels -----------------------------------------------------------------

def test_loading_a_missing_level_raises_a_readable_error():
    expect_value_error(
        lambda: storage.load_level("there_is_no_such_level.json"), "Could not find"
    )


# -- saving and loading designs ---------------------------------------------

def test_a_saved_design_can_be_loaded_again():
    plan = FloorPlan(12, 10)
    plan.paint((1, 1, 4, 3), "bedroom")
    plan.paint((6, 1, 3, 3), "kitchen")
    plan.add_wall(wall_key((2, 1), (3, 1)))

    try:
        storage.save_design(TEMPORARY_FILE, plan, "compact_apartment")
        design = storage.load_design(TEMPORARY_FILE)

        assert design["level"] == "compact_apartment"
        assert design["tiles"] == plan.tiles
        assert design["walls"] == plan.walls
    finally:
        remove_temporary_file()


# -- TODO 22: write these ---------------------------------------------------
#
# expect_value_error() above takes a function, so pass it a lambda:
#     expect_value_error(lambda: storage.load_design("nope.json"), "Could not find")
#
# Levels
#   test_a_real_level_file_loads
#       (load "compact_apartment.json" and check a couple of its values)
#
# Saving and loading
#   test_a_loaded_design_rebuilds_the_same_rooms
#       (paint a block, wall it into two rooms, save, load into a fresh
#        FloorPlan, and check it still finds two rooms.  Remember to call
#        design_changed() after setting .tiles and .walls directly)
#   test_an_empty_design_saves_and_loads
#
# Broken files - use write_temporary_file() to make the bad file first
#   test_loading_a_missing_design_raises_a_readable_error
#   test_loading_a_damaged_json_file_raises_a_readable_error
#       (write  { this is not valid JSON at all )
#   test_loading_a_design_with_a_missing_tile_list_raises_an_error
#   test_loading_a_tile_with_an_unknown_room_type_raises_an_error
#   test_loading_a_tile_with_a_missing_coordinate_raises_an_error
#   test_loading_a_wall_between_tiles_that_do_not_touch_raises_an_error
