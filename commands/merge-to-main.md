---
description: Run tests, commit staged work, and merge current branch to main via worktree
allowed-tools:
  - Bash(git *)
  - Bash(uv run *)
  - Bash(npm test*)
  - Bash(cargo test*)
  - Bash(bd *)
  - Read
---

# Merge to Main

Complete the current branch's work and land it on main. Run every step sequentially — do not skip steps or ask for confirmation.

## Step 0: Detect branch

```bash
git branch --show-current
```

If on `main`, Steps 2, 4, and 5 are skipped (no merge needed — you're already there).

## Step 1: Commit any uncommitted changes

Commit first so the merge in Step 2 never runs against a dirty tree.

Check `git status`. If there are staged or modified tracked files:

```bash
git add <relevant files>
git commit -m "<conventional commit message summarizing changes>"
```

Do NOT commit untracked files unless they are clearly part of the current work.

If the working tree is clean, skip this step.

## Step 2: Pull from main (worktree branches only)

```bash
git merge main
```

If this fails with a conflict, STOP and report the conflict to the user.

## Step 3: Run tests

Test the combined result (your work plus the latest main). Detect the project type and run the appropriate test command:

- If `pyproject.toml` exists → `uv run --frozen pytest`
- If `package.json` exists → `npm test`
- If `Cargo.toml` exists → `cargo test`
- If none found → warn "No recognized test runner found" and continue

If tests fail, STOP and report failures to the user. Do not proceed with a broken build.

## Step 4: Merge to main (worktree branches only)

Skip this step if already on `main`.

```bash
MAIN_WT=$(git worktree list --porcelain | awk '/^worktree /{path=$2} /branch refs\/heads\/main/{print path}')
BRANCH=$(git branch --show-current)
git -C "$MAIN_WT" merge "$BRANCH" --ff-only
```

A fast-forward cannot conflict, so if this fails either main has diverged (below) or the main worktree has uncommitted changes touching the same files — in that case STOP and report; do not stash or discard them.

### If `--ff-only` fails because main has diverged:

1. Repeat Step 2 (`git merge main`) and Step 3 (tests).
2. If tests pass, retry the `--ff-only` merge above.
3. If it still fails, STOP and report the situation to the user.

## Step 5: Push (worktree branches only)

Skip this step if already on `main`. Push only when main has an upstream; local-only repos skip it too.

```bash
if git -C "$MAIN_WT" rev-parse --abbrev-ref main@{upstream} >/dev/null 2>&1; then
  git -C "$MAIN_WT" push
fi
```

Report the resulting main commit.

## Step 6: Close beads issues

Close the bead(s) you worked on in this session:

```bash
bd close <id1> <id2> ...
```

If already closed earlier in the conversation, skip this step.
