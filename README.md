# Floor Plan Challenge — starting point

A small architectural design game built with Python and Pygame.

A fictional client gives you a brief. The player paints rooms onto a grid by
dragging with the mouse, and the game checks the design as it is built: room
sizes, adjacency, the building outline, and the budget. Submitting the design
gives a score.

Rooms are not rectangles. Painting a bedroom next to an existing bedroom grows
that bedroom, the way a real floor plan works. To turn one big room into two,
draw a wall through it.

Some of this project is written for you. The rest is yours.

## Running it

```
pip install pygame
python main.py
```

If Pygame will not install, check your Python version — Pygame 2.6 does not
work on Python 3.14. Use Python 3.10 to 3.13.

**The game runs before you write a line of code.** Try it now. Then open
[TODO_GUIDE.md](TODO_GUIDE.md), which lists all 22 TODOs in completion order.

## How to play

1. Pick a client from the level select screen.
2. Choose a room type from the palette on the right.
3. Drag on the grid to paint. The preview turns green when the area is free
   and red when it already belongs to a different room.
4. Painting next to a room of the same type joins them into one room.
5. Use the **Wall** tool to split a room in two: drag along the tile edges
   where the wall should go. Starting a drag on an existing wall rubs walls
   out instead, so one tool does both.
6. Use the **Erase** tool to clear tiles, for trimming a shape back.
7. Click a room to select it, then press Delete to remove all of it.
8. Press **Check Design** when you are done.

Keyboard shortcuts: `1`–`4` pick a room type, `E` erase, `W` wall, `Delete`
removes the selected room, `S` saves, `L` loads, `Enter` checks the design,
`Esc` goes back to the level list.

## Running the tests

```
python run_tests.py
```

Every function in `tests/` whose name starts with `test_` is run, and you get
a pass or fail line for each one. A test passes when it finishes without an
`AssertionError`.

## What is written for you, and what is yours

| File | |
|---|---|
| `main.py` | given — starts the program |
| `constants.py` | given — sizes, colours, room types, scoring weights |
| `renderer.py` | given — all the drawing |
| `game.py` | given — the loop, the events, the tools, the buttons |
| `run_tests.py` | given — the test runner |
| `levels/*.json` | given — three client briefs |
| `grid.py` | **TODO 1–2** — pixels to tiles and back |
| `room.py` | **TODO 3–5** — one room, as a set of tiles |
| `floor_plan.py` | **TODO 6–10** — painting, erasing, and what a room costs |
| `rules.py` | **TODO 11–16** — the rules of the grid, and the client's requirements |
| `storage.py` | **TODO 17–21** — files and JSON |
| `tests/*.py` | **TODO 22** — your tests |

Do them **in number order**, one file at a time. That order is worked out so
that every step changes what you see on screen, and so that you never need a
function you have not written yet. [TODO_GUIDE.md](TODO_GUIDE.md) walks
through it step by step and tells you what to look for after each one.

Read `renderer.py` and `game.py` even though you are not changing them. You
will be asked to explain how the program fits together, and those two files
are where the answer lives.

## How the modules fit together

```
main.py
   |
   v
 Game  ------------------------------.
   |                                 |
   +-- FloorPlan                     +-- Renderer  (draws everything)
   |      |                          |        |
   |      `-- Room objects           |        `-- grid.py  (pixels <-> tiles)
   |                                 |
   +-- rules.py    (finds the rooms, judges the design)
   |
   `-- storage.py  (levels in, designs out)
              |
              `-- levels/*.json
```

Two things to notice, because they are the reason the project is split up
this way:

- **`rules.py` never imports Pygame.** That is what lets you test the rules
  without opening a window.
- **`renderer.py` never decides anything.** It is handed the answers and puts
  them on screen. If you ever find yourself wanting to work out whether an
  area can be painted inside a drawing function, that is the signal the code
  belongs somewhere else.

## How rooms are worked out

The program stores the **grid**, not the rooms: a dictionary mapping each
painted tile to its room type, plus a set of the walls the player has drawn.

Rooms are found on demand by `rules.find_rooms()` — a flood fill that groups
tiles joined to each other. That function is written for you, but it is built
on two things you write, `neighbours()` and `tiles_are_joined()`, so nothing
about rooms works until those do.

Because rooms are derived from the grid rather than stored, they can never
disagree with it.

## Where things live

Adding a room type? `ROOM_TYPES` in `constants.py`. Adding a level? A new file
in `levels/` plus its name in `LEVEL_FILES`. Neither needs a change to the
game logic — that is the point of keeping them as data.

## Getting the code, and handing it in

You work in Git. Full instructions are in
[GIT_WORKFLOW.md](GIT_WORKFLOW.md) — read it once before you start.

The short version:

```
git clone <the repository address>      # once, at the start
cd FloorPlan

# ... write some code ...

git add -A                              # stage what you changed
git commit -m "TODO 1: screen_to_grid"  # save it, with a message
git push                                # send it to GitHub
```

**Commit after every TODO.** Twenty-two small commits with real messages are
worth far more to you — and are far easier to un-break — than one enormous
commit at the end. Your commit history is part of what is being marked.

If the starting code is ever corrected, you will be told to run `git pull` to
collect the change.

## What to hand in

Push all of it to the `main` branch of your repository:

- The finished program, with all 22 TODOs done.
- 12 to 20 tests that pass.
- A README of your own describing what you built, what you added beyond the
  TODOs, anything still broken, and one bug that took you a while.
- A commit history that shows the work happening in steps.