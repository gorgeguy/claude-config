---
description: Fresh-eyes audit of all open beads for stale references, inconsistencies, broken epic/dependency structure, and missing test plans, then fix the defects
---

# Fresh-Eyes Bead Audit

You are a fresh-eyes auditor. You have NO prior context about this project or these beads. Your job is to read every open bead issue and produce a structured defect report, then fix everything you find.

## Phase 1: Gather

1. Run `bd list --status=open` and `bd blocked` in parallel.
2. Read every open issue with one `bd show <id1> <id2> ...` call (it accepts many ids). Do not fan this out to subagents: a subagent that returns full `bd show` output puts the same text into your context and adds only latency.
3. For code verification in Phase 2, spawn a separate Agent (subagent_type=Explore) to spot-check the 2-3 highest-severity code claims against actual source files — that search is the part worth keeping out of your context.

## Phase 2: Audit Each Issue

For each issue, check for these defect categories:

### Accuracy
- **Stale references** — Does the text mention ticket IDs, letter codes, or issue names that don't exist or are closed? Cross-check against `bd list`.
- **Code claim verification** — For any claim about specific code (line numbers, function signatures, field names), spot-check 2-3 of the highest-severity issues against actual source code. Flag any claim that is wrong.
- **Count discrepancies** — Do counts in descriptions ("six findings", "20 functions") match reality?

### Consistency
- **Description vs Notes contradiction** — Does the Notes section say something different from the Description? (e.g., different acceptance criteria, different dependency references, different line counts)
- **Test plan duplication** — Are the same tests listed in both Description and Notes? If so, which is canonical?
- **Acceptance Criteria vs Implementation Plan** — Is anything in AC not covered by the plan, or vice versa?

### Structure
- **Epic coherence (mechanical check, not prose)** — For every epic in this run:
  - Run `bd list --parent <epic-id>`. The output MUST list every task that
    belongs to this epic. If it shows zero or fewer children than expected,
    the `--parent` field was never set on the children — a description-body
    line like `Epic: <id>` does NOT count and is the most common failure mode.
    Recommended fix: `bd update <child-id> --parent <epic-id>` for each missing
    child.
  - Run `bd epic status <epic-id>`. It MUST report a non-zero child count and
    accurate progress. "No open epics found" against a clearly-open epic is a
    symptom of the same missing-parent defect.
  - Cross-reference: do epic ACs match their open children? Are any AC items
    satisfied by closed children without being marked?
- **Dependency graph correctness** — Does the "Serialized resource" and
  "Parallelizable" field match the actual BLOCKS/DEPENDS ON? Are there
  dependencies on closed tasks? Note: `bd dep` (blocking) and `--parent`
  (hierarchy) are independent — a ticket can have correct sibling deps but
  still be missing its parent edge, and vice versa. Check both.
- **Sibling DAG matches the plan** — For each workstream, identify the
  terminal fan-in ticket (smoke/verify/integration step) and run
  `bd dep tree <id>`. The tree must reproduce the plan's prereq graph: every
  ticket the plan says blocks the smoke step should appear upstream of it.
  Missing nodes mean either an unticketed plan item or a missed `bd dep add`.
- **Completion protocol accuracy** — Do completion protocols reference the
  correct downstream ticket IDs? Cross-check with actual BLOCKS shown in
  `bd show`.

### Completeness
- **Missing test plans** — Does every implementation task have specific, named test scenarios?
- **Missing information** — Is any section empty or says "TBD" without a clear dependency on another ticket that will fill it?
- **Readability** — Could an implementer with zero context follow the instructions and know exactly what to do?

## Phase 3: Report

Output a structured report with:

### Per-issue table
| ID | Title | Defects | Severity |
For each defect, one line with: defect type, specific text that's wrong, recommended fix.
Mark clean issues as "CLEAN".

### Summary statistics
- Total issues audited
- Clean vs defective
- Defect count by category
- Defect count by severity (HIGH/MEDIUM/LOW)

### Recommended fixes (prioritized)
Group by severity. For each fix, specify the exact `bd update` command or action needed.

## Phase 4: Fix (if defects found)

After presenting the report, execute all fixes without asking — the audit's job is to leave the graph healthy, and every fix is a reversible `bd update`/`bd dep` edit. Stop and ask only for a fix that would close or delete an issue. Each fix is a single `bd` command, so run them directly — issue independent commands as parallel tool calls rather than spawning subagents. Order only the fixes that depend on each other (e.g., `bd dep remove` before `bd close`). Afterwards, re-run `bd blocked` and `bd ready` to verify the graph is healthy.

## Guidelines

- Be pedantic. Report everything, even LOW-severity issues.
- Never skip an issue — audit ALL open issues.
- For code verification, only spot-check the 2-3 most critical claims. Don't read every file.
- If the bead system has no open issues (`bd list --status=open` returns nothing), report "No open beads to audit" and exit.
- Batch reads (`bd show` with many ids) and run independent commands as parallel tool calls for speed.
