# Working with Git on this project

Everything you hand in goes through Git. This page is the reference — read it
once now, then come back to it when something goes wrong.

---

## The idea in one picture

```
   GitHub  (the remote, nicknamed "origin")
      ^  |
 push |  | pull / clone
      |  v
   your computer  (your local repository)
      ^  |
commit|  | checkout
      |  v
   your files  (the working tree — what your editor sees)
```

Three separate places. Saving a file in your editor changes **only** the
working tree. `git commit` records it in your **local repository**.
`git push` sends it to **GitHub**. Nothing reaches GitHub until you push, and
your teacher cannot see work you have not pushed.

---

## Setting up, once

```
git clone https://github.com/<your-teacher>/FloorPlan.git
cd FloorPlan
```

`clone` does four things at once: downloads the project, creates the local
repository, names the address it came from **`origin`**, and checks out the
`main` branch.

Tell Git who you are, so your commits carry your name:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

---

## The loop you will repeat 22 times

```
python main.py                     # see what is broken
# ... write one TODO ...
python run_tests.py                # check it

git status                         # what have I changed?
git diff                           # what exactly did I change?
git add -A                         # stage all of it
git commit -m "TODO 1: screen_to_grid maps pixels to tiles"
git push
```

**Commit after every TODO.** A commit is a save point you can return to. If
you break something badly, a commit from ten minutes ago is the difference
between losing ten minutes and losing an evening.

### Writing a commit message

Say what the commit *does*, not that you did work.

| Good | Bad |
|---|---|
| `TODO 12: tiles_are_joined checks walls and room type` | `update` |
| `Fix rooms leaking diagonally in neighbours()` | `fixed bug` |
| `Add test for erasing splitting a room in two` | `stuff` |

---

## `git push` vs `git push origin main`

These usually do the same thing. Understanding the difference is worth five
minutes.

`git push origin main` is the **explicit** form. It says: *take my `main`
branch, and send it to the branch called `main` on the remote called
`origin`.* There is no guesswork.

`git push` is the **short** form. It works only when Git already knows where
your branch belongs — when your branch has an **upstream** (also called a
tracking branch). `git clone` sets that up for `main` automatically, which is
why plain `git push` works from your first day.

Check what your branch is tracking:

```
git branch -vv
```

```
* main  a3f1c9d [origin/main] TODO 1: screen_to_grid maps pixels to tiles
                 ^^^^^^^^^^^^ this is the upstream
```

If you make a **new** branch, it has no upstream yet, and plain `git push`
will refuse and tell you so:

```
fatal: The current branch experiment has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin experiment
```

Git is telling you the exact command to run. `--set-upstream` (short: `-u`)
pushes *and* records the link, so from then on plain `git push` works on that
branch too.

> **Habit worth having:** use `git push origin main` when you are not sure,
> and read what Git prints. The explicit form never pushes somewhere you did
> not mean.

---

## `git pull`

`git pull` brings changes from GitHub down to you. You need it when:

- your teacher fixes something in the starting code and tells you to pull, or
- you have been working on two machines (school and home).

```
git pull
```

That is really two commands in one: `git fetch` (download what is on the
remote) followed by `git merge` (join it into your branch).

**Pull before you start work**, especially if you also work at home. It is far
easier to merge one day of changes than two weeks of them.

### If a pull conflicts

Git stops and marks the clash inside the file:

```python
<<<<<<< HEAD
    return (grid_x, grid_y)
=======
    return (int(grid_x), int(grid_y))
>>>>>>> origin/main
```

`HEAD` is your version; below the `=======` is theirs. Fix it by hand:
delete the three marker lines and leave the code you want. Then:

```
git add grid.py
git commit
```

Nothing is lost and nothing is broken — Git has simply refused to guess.

---

## Branches, briefly

A branch is a movable name for a line of commits. `main` is just the branch
`clone` gave you; there is nothing magic about the name.

```
git branch                       # list branches, * marks the current one
git switch -c try-new-colours    # create a branch and move onto it
git switch main                  # go back
```

Branches are useful here for one thing in particular: **trying something
risky without endangering working code.** If you want to rewrite the renderer
for your extension, do it on a branch. If it works, merge it:

```
git switch main
git merge try-new-colours
```

If it does not, abandon it — `main` never changed.

For this project you can do everything on `main` and be fine. Use a branch
when you catch yourself thinking "I hope I don't break this."

---

## Hand-in

Your work is handed in when it is **pushed to `main`**. Check it really is:

```
git status
```

- `nothing to commit, working tree clean` — everything is committed.
- `Your branch is up to date with 'origin/main'.` — everything is pushed.

If it says `Your branch is ahead of 'origin/main' by 3 commits`, those three
commits exist only on your laptop. Push them.

Then open the repository on GitHub in a browser and look. If you can see your
code there, it is handed in.

---

## When something goes wrong

| Situation | Command |
|---|---|
| What have I changed? | `git status`, then `git diff` |
| Undo changes to one file I have not committed | `git restore grid.py` |
| I staged something by mistake | `git restore --staged grid.py` |
| What have I committed? | `git log --oneline` |
| Look at an old version of a file | `git show <commit>:grid.py` |
| Push rejected, "fetch first" | someone pushed before you: `git pull`, fix any conflict, push again |

**Never** solve a Git problem by deleting the folder and re-cloning. You lose
your history, which is part of what is being marked. Ask instead — every
mistake on this list is recoverable.
