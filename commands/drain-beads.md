---
description: Iteratively launch a worker sub-agent to claim and complete ready beads until the queue is drained
argument-hint: "[optional filter clause, e.g. \"with label 'aws-props' \"]"
allowed-tools:
  - Agent
  - Bash(bd *)
  - Bash(mkdir *)
  - Bash(date *)
  - Bash(git rev-parse *)
  - Bash(test *)
  - Bash(rm *)
  - Read
  - Write
  - Edit
  - ScheduleWakeup
---

# Drain Beads

You are a **driver agent** that iteratively dispatches a worker sub-agent to claim and complete ready beads. You do **not** do the work yourself — you only launch sub-agents, read their summaries, and decide whether to continue.

## Parameters

- `filter_clause` = `$ARGUMENTS` (optional; may be empty — treat as empty string if unset)

## Setup (do this once, at start)

1. Resolve the repo root, the log file, and the stop-sentinel path:
   ```bash
   REPO=$(git rev-parse --show-toplevel)
   TS=$(date +%Y%m%d-%H%M%S)
   mkdir -p "$REPO/.claude/logs"
   LOG="$REPO/.claude/logs/drain-beads-$TS.md"
   STOP="$REPO/.claude/logs/drain-beads.stop"
   ```
2. Clear any stale stop-sentinel from a previous run so the fresh run isn't pre-stopped: `rm -f "$STOP"`.
3. Initialize `$LOG` with a header: the timestamp, the `filter_clause` value (or `(none)` if empty), and a "Summaries" section.
4. Report **both** paths to the user on one line each — the log path (for tailing) and the stop path (so they know what to `touch` to halt the loop).
5. Initialize `empty_streak = 0`, `iter = 0`.

## Loop protocol

**Sequentiality is mandatory.** You must launch exactly ONE sub-agent per iteration, wait for it to return, and only then decide whether to launch the next one. Do not:
- Launch a second `Agent` call in the same tool-use block as the first.
- Start the next iteration before the previous sub-agent has returned a result.
- Run the sub-agent with `run_in_background=true`.
- Speculatively pre-launch sub-agents "in case" the current one reports EMPTY.

The reason: all sub-agents in this run share a single git working tree, so two of them cannot safely check out branches, edit files, commit, or run independent test suites concurrently. The `claim-bead` step itself (which runs `bd ready --claim --actor <worktree>`) is atomic and safe — `bd ready --claim` selects and claims in a single transaction, skipping beads already owned by another worktree — but the post-claim work forces serial execution.

Each iteration:

1. Increment `iter`.
2. **Stop-file check (first thing, before anything else).** Run `test -f "$STOP"` via `Bash`. If the file exists, the user has requested a halt — stop cleanly:
   - Remove the sentinel: `rm -f "$STOP"` (so it doesn't linger and pre-stop the next run).
   - Append to `$LOG`:
     ```
     ---
     Terminated: stop sentinel detected at iter <N>.
     ```
   - Report to the user: "Stop sentinel detected — halting. Log: `$LOG`" and exit the loop.
   - Do **not** launch a sub-agent this iteration.
3. Launch ONE `Agent` call with `subagent_type=general-purpose` and the **worker prompt** below (verbatim — substitute `${filter_clause}` with the parameter value, which may be the empty string). Run it in the **foreground** (default — do not pass `run_in_background`). The `Agent` call blocks until the sub-agent returns; do not issue any other tool calls in that same block.
4. When the sub-agent returns, classify its result:
   - **CLAIMED** — the sub-agent reports it claimed a bead (whether or not it ultimately closed it). Append to `$LOG`:
     ```
     ## iter <N> — <bd-id> — <status: closed | blocked | in_progress>
     <full "Summarize the fix and validations" text from the sub-agent>
     ```
     Reset `empty_streak = 0`.
   - **EMPTY** — `claim-bead` reported no ready bead to claim (none match the filters, or all matches are blocked or already owned by another worktree). Append a one-liner to `$LOG`:
     ```
     - iter <N>: EMPTY (streak=<K>)
     ```
     Increment `empty_streak` by 1.
5. Print one line to the user: `iter N: CLAIMED <bead-id> — <one-line summary>` or `iter N: EMPTY (streak=K)`.
6. Decide next step:
   - If `empty_streak >= 10`: stop. Append a final line to `$LOG`:
     ```
     ---
     Terminated: 10 consecutive empty attempts — queue drained.
     ```
     Report to the user: "No ready beads claimed in 10 consecutive attempts — queue appears drained. Log: `$LOG`" and exit the loop.
   - Else if last result was **EMPTY**: use `ScheduleWakeup` with `delaySeconds=240` and `prompt` = the verbatim slash-command invocation the user ran (e.g. `/drain-beads $ARGUMENTS`). Give a one-sentence `reason` like "idle poll — waiting for new ready beads (streak=K/10)".
   - Else (**CLAIMED**): launch the next iteration immediately — no sleep.

Keep your own user-facing output terse: one line per iteration plus the initial log-path announcement and final drain message. Do not re-summarize the sub-agent's work inline, do not inspect the repo yourself, do not run `bd` commands directly — the worker handles all of that.

## Log ownership

**You (the driver) are the sole writer of `$LOG`.** The sub-agents you launch do not know the log path, are not told about it, and must not be instructed to touch it. The sub-agent's contract is: produce its "Summarize the fix and validations" text in its final return message. You extract that text from the return value and append it to `$LOG` yourself using `Write`/`Edit` (or `Bash` with `>>` if you prefer, but keep it to the driver).

This is deliberate:
- Sub-agents are launched fresh each time and would have no reliable way to locate the log.
- A single writer removes any chance of interleaved or out-of-order entries.
- Classification (CLAIMED vs EMPTY) happens in the driver anyway, so structuring the log entry belongs there too.

If a sub-agent's return message is malformed or missing a summary, write a best-effort entry (`<no summary returned>`) and keep looping — do not re-launch a sub-agent just to regenerate a summary.

## Classification heuristics

When reading the worker's return message:
- If it contains `Claimed issue: <id>` (`claim-bead`'s success line), or names a claimed bead id together with any of "closed", "merged", "blocked", "in_progress" → **CLAIMED**. Bead ids carry the workspace's own issue prefix (e.g. `myproject-a1b2`), not necessarily `bd-`, so never key on the prefix.
- If it says "No ready work to claim" (`claim-bead`'s message when nothing is claimable), "no ready bead", or "queue empty" → **EMPTY**.
- If ambiguous, prefer **EMPTY** — it's safer to over-count empty streaks than to spin forever on unclear signals.

## Worker prompt (pass to each sub-agent, verbatim)

```
Claim the next ready bead ${filter_clause} by running 'claim-bead'. It atomically
claims the highest-priority ready bead via 'bd ready --claim', as the current
worktree, and already excludes 'human'-labeled beads and anything in_progress —
so do NOT list, hand-pick, or handle claim races yourself.

If a condition is shown above, append it to 'claim-bead' as 'bd ready' filter flags:
  - already in flag form (--label X, --parent P, ...) -> pass through unchanged
  - "with label X" / a bare term                      -> --label X
  - "with parent P" / "under P" (P is a bead/epic id) -> --parent P
  - "with any of labels A, B"                         -> --label-any A,B
  - "of type bug|feature|task|..."                    -> --type <type>
  - "priority N" / "PN"                               -> --priority N

If 'claim-bead' prints "No ready work to claim", report that and do nothing else.

Otherwise it prints the claimed bead id. Then:
1. Read the full ticket with 'bd show <id>' — satisfy all exit criteria
2. Implement the fix, run tests, run linting
3. If you discover bugs or related work, file new issues linked with discovered-from
4. If you believe this bead should be reviewed by a human, set status to blocked with explanation and stop
5. If otherwise blocked, set status to blocked with explanation and stop
6. Follow applicable repository and user instructions for completion. Do not infer an integration target from Git's tracking upstream. Do not manipulate stashes. If no explicit landing target or authority exists, leave the bead in progress and report the tested commit for the landing coordinator.
7. Close the bead only after all repository completion criteria, including any required landing and final integrated tests, are satisfied.
8. Summarize the fix, tested commit, and validations.
```
