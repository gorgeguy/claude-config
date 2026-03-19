---
description: Run tests, commit staged work, and merge current branch to main via worktree
allowed-tools:
  - Bash(git *)
  - Bash(uv run *)
  - Bash(bd *)
  - Bash(git-merge-to-main*)
  - Read
---

# Merge to Main

Complete the current branch's work and land it on main. Run every step sequentially — do not skip steps or ask for confirmation.

## Step 0: Detect branch

```bash
git branch --show-current
```

If on `main`, skip to **Step 3** (no merge needed — you're already there).

Otherwise, continue with Step 1.

## Step 1: Pull from main (worktree branches only)

```bash
git merge main --ff
```

If this fails with a conflict, STOP and report the conflict to the user.

## Step 2: Run tests

```bash
uv run --frozen pytest
```

If tests fail, STOP and report failures to the user. Do not proceed with a broken build.

## Step 3: Commit any uncommitted changes

Check `git status`. If there are staged or modified tracked files:

```bash
git add <relevant files>
git commit -m "<conventional commit message summarizing changes>"
```

Do NOT include `Co-Authored-By` lines. Do NOT commit untracked files unless they are clearly part of the current work.

If the working tree is clean, skip this step.

## Step 4: Merge to main (worktree branches only)

Skip this step if already on `main`.

```bash
git-merge-to-main
```

**Note:** `git-merge-to-main` runs `git push` after merging. If no remote is configured, the push fails with exit code 128 even though the merge succeeded. Check the output — if you see `Fast-forward` and the file change summary, the merge worked. Ignore the push error in local-only repos.

If this succeeds, report success and the merge commit.

### If `--ff-only` fails (main has diverged):

1. Merge main into the work branch:
   ```bash
   git merge main --ff
   ```
2. Re-run tests:
   ```bash
   uv run --frozen pytest
   ```
3. If tests pass, recommit if the merge created changes, then retry:
   ```bash
   git-merge-to-main
   ```
4. If it still fails, STOP and report the situation to the user.

## Step 5: Close beads issues

Close the bead(s) you worked on in this session:

```bash
bd close <id1> <id2> ...
```

If already closed earlier in the conversation, skip this step.
