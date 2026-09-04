# Your TODO list, in order

There are 22 TODOs. They are numbered in the order you should do them, so
**TODO 1 first, TODO 22 last**, and nothing you write will ever depend on
something you have not written yet.

They are also grouped into six steps, one file at a time. **Every step
changes what you see on screen.**

The point of this project is for you to practice what you learned so far, learn
some new things along the way, and see your changes improve the game piece by piece.

---

## Before you start: run the game

```
python main.py
```

It works. The window opens, you pick a client, the grid draws, the palette
and tools draw, the requirement list is there, the budget reads $0. Nothing
crashes.

That is on purpose. Every unfinished function returns a sensible empty answer
— `0`, `False`, `[]`, `None` — instead of crashing the program.

Try this now, before writing anything:

- Drag on the grid. A green preview appears in the **top-left corner** no
  matter where your mouse is. That is TODO 1.
- Let go. Nothing is painted. That is TODO 7.
- Look at the requirement list. Every line says FAIL except "Stay within the
  budget", which passes because the design costs $0.

---

## Step 1 — the mouse finds the grid (TODO 1–2, `grid.py`)

`screen_to_grid`, `is_inside_grid`.

`grid_to_screen()` is written for you, six lines above `screen_to_grid()`. It
does the same job in the opposite direction. Read it first.

**Run the game. You should now see:** the drag preview appears *where your
mouse actually is*, and grows and shrinks as you drag, with its size and cost
written above it — `4 x 3 = 12 tiles $72,000`.

Try dragging up and to the left, and try dragging off the edge of the grid.
Both should behave. `rectangle_from_drag()` is written for you and its comment
explains why.

Letting go still paints nothing. That comes in step 2.

---

## Step 2 — painting (TODO 3–10, `room.py` then `floor_plan.py`)

This is the step that turns the game on. Do the two files in order.

### 2a. `room.py` (TODO 3–5) — `area`, `cost`, `contains_grid_position`

**This one you check with tests, not with your eyes.** Nothing can be painted
yet, so there is nothing on screen for a room to be. Once you finish these TODOs,
open the command line from the project folder and run:

```
python run_tests.py
```

`test_area_is_the_number_of_tiles` should go from FAIL to pass.

You won't see any visual changes in the game yet as we are purely working on some of the 
logic in this step.

### 2b. `floor_plan.py` (TODO 6–10) — `paint_error`, `paint`, `erase`, `room_at_position`, `total_cost`

**After you complete these TODOs, run the game. You should now see:**

- Dragging **paints rooms**. Color appears on the grid.
- Dragging a different room type over an existing room is **refused**, with a
  red preview and the message *"That area is already part of another room."*
- The **Erase** tool clears tiles.
- Clicking a room **selects it** — a yellow outline, and the sidebar fills in
  `SELECTED ROOM`. The **Delete** button stops being grayed out.

**Two things will look wrong, and both are correct for now:**

1. The sidebar says the room you clicked is **1 tiles**, and each square keeps
   its own dark outline instead of merging into one shape. Every single tile
   is its own room, because `tiles_are_joined()` still says no to everything.
   Step 3 fixes it.
2. The **budget still reads $0**, even though `total_cost()` is written. It
   calls `rules.calculate_total_cost()`, which is still a stub. Step 3 fixes
   that too.


---

## Step 3 — tiles become rooms (TODO 11–14, `rules.py`)

`neighbours`, `tiles_are_joined`, `rectangle_is_inside_plan`,
`calculate_total_cost`.

Write `neighbours` and `tiles_are_joined` first. `find_rooms()` is written for
you, but it is built on both of them, so nothing about rooms works until they
do.

**Run the game. You should now see the picture snap together:**

- Tiles **merge**. Painting a bedroom beside an existing bedroom grows that
  bedroom into one shape with one outline.
- Room **labels appear** — `Bedroom` with `12 tiles` under it. (A room needs
  at least 4 tiles to have room for its label.)
- The **Wall** tool splits one room into two. Drag along the tile edges; drag
  along an existing wall to rub it out.
- The **budget bar fills up** and the number counts your real cost.

`tiles_are_joined` is four lines and decides the entire behaviour of the game.
It is why painting beside a bedroom grows that bedroom, and why a wall splits
one room in two. If rooms leak into each other diagonally, look at
`neighbours`.

---

## Step 4 — the client is watching (TODO 15–16, `rules.py`)

`rooms_are_adjacent`, then `check_one_requirement` — four more requirement
kinds, with two worked examples already there to copy.

**Run the game. You should now see:** the requirement list ticking over to
PASS as you build, and **Check Design** giving a real score instead of zero.

Add one requirement kind at a time and watch one more line come alive. The
practice brief you have been looking at has one of each kind, so all four show
up immediately:

| Line | Needs |
|---|---|
| Include 2 bedrooms | `room_count` |
| Every bedroom is at least 12 tiles | `minimum_area` |
| The kitchen opens onto a living room | `adjacent` |
| The bathroom does not open onto the kitchen | `not_adjacent` |

`rooms_are_adjacent` is the hardest function in the project. The last two
lines need it.

---

## Step 5 — files (TODO 17–21, `storage.py`)

`read_json_file`, `load_level`, `tiles_from_data`, `save_design`,
`load_design`.

**Run the game. You should now see:** the **three real client briefs** on the
level select screen, each with its own name, brief, plan size, budget and
requirement list — instead of three copies of the practice brief you have
been working against. Then Save and Load working: paint something, press `S`,
quit, start again, press `L`, and get it back.

Try breaking things on purpose:

- Delete `levels/family_home.json` and start the game. The other two levels
  should still work and the missing one should be reported on screen, not
  crash the program. `load_all_levels()` is written for you — read it to see
  how, then make sure your `load_level` raises the `ValueError` it expects.
- Open your save file in a text editor and mangle it. Load it. You should get
  a readable message, not a traceback.

---

## Step 6 — tests (TODO 22, `tests/`)

Write the tests listed in the four test files. You need **12 to 20**; the
lists give you more than that, so choose.

Run them with `python run_tests.py`. Every function whose name starts with
`test_` is run, and a test passes when it finishes without an
`AssertionError`.

Watch out for tests that pass for the wrong reason. In `tests/test_rules.py`
two of the worked examples pass against the *unfinished* code, because a
function that answers `False` about everything happens to satisfy them. A
test only tells you something if it could have failed.

---

## Rules of thumb

- **Run the game after every TODO.** A bug found one function after you wrote
  it takes a minute. A bug found ten functions later takes an hour.
- **Stubs return empty answers, not `None`.** If you leave one unfinished the
  program still runs, so trust what you *see* over what you assume.
- **`design_changed()` is easy to forget.** `FloorPlan` remembers its room
  list so it does not redo the flood fill sixty times a second. Every method
  that edits tiles or walls has to throw that memory away, or the screen keeps
  showing the old rooms. There is a test listed for exactly this.
- **Do not touch `renderer.py`, `game.py`, or `constants.py`** until every
  TODO is done. Then go wild — colours, fonts, a title screen, new room types
  in `ROOM_TYPES`, new levels in `levels/`. None of that needs new logic, and
  it is where the project starts to look like yours.
- **Do not edit the level JSON files** to make a requirement easier to pass.
  Fix the code instead.

---

## The whole list at a glance

| # | File | Function | Done when you see |
|---|---|---|---|
| 1 | `grid.py` | `screen_to_grid` | preview follows the mouse |
| 2 | `grid.py` | `is_inside_grid` | clicks beside the grid are ignored |
| 3 | `room.py` | `area` | *(tests)* |
| 4 | `room.py` | `cost` | *(tests)* |
| 5 | `room.py` | `contains_grid_position` | *(tests)* |
| 6 | `floor_plan.py` | `paint_error` | overlaps refused, with a reason |
| 7 | `floor_plan.py` | `paint` | rooms appear when you drag |
| 8 | `floor_plan.py` | `erase` | the Erase tool clears tiles |
| 9 | `floor_plan.py` | `room_at_position` | clicking selects a room |
| 10 | `floor_plan.py` | `total_cost` | *(still $0 until 14)* |
| 11 | `rules.py` | `neighbours` | tiles stop being separate rooms |
| 12 | `rules.py` | `tiles_are_joined` | rooms merge; walls split them |
| 13 | `rules.py` | `rectangle_is_inside_plan` | painting stays in the building |
| 14 | `rules.py` | `calculate_total_cost` | the budget bar fills |
| 15 | `rules.py` | `rooms_are_adjacent` | adjacency requirements work |
| 16 | `rules.py` | `check_one_requirement` | the requirement list goes green |
| 17 | `storage.py` | `read_json_file` | broken files give readable errors |
| 18 | `storage.py` | `load_level` | the three real briefs appear |
| 19 | `storage.py` | `tiles_from_data` | a saved design loads its rooms |
| 20 | `storage.py` | `save_design` | Save writes a file |
| 21 | `storage.py` | `load_design` | Load brings your design back |
| 22 | `tests/` | your tests | 12–20 of them passing |
