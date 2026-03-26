# Fresh-Eyes Bead Audit

You are a fresh-eyes auditor. You have NO prior context about this project or these beads. Your job is to read every open bead issue and produce a structured defect report, then fix everything you find.

## Phase 1: Gather

1. Run `bd list --status=open` to get all open issues and `bd blocked` in parallel
2. You MUST use the Agent tool to spawn parallel subagents to read issues. Batch issues into groups of 4-5 and spawn one Agent per group. Each agent should run `bd show <id>` for its assigned issues and return the full output. Do NOT read issues sequentially — the whole point of this phase is speed.
3. For code verification in Phase 2, spawn a separate Agent (subagent_type=Explore) to spot-check the 2-3 highest-severity code claims against actual source files

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
- **Epic coherence** — Do epics have their child tasks linked (CHILDREN section in `bd show`)? Do epic ACs match their open children? Are any AC items satisfied by closed children without being marked?
- **Dependency graph correctness** — Does the "Serialized resource" and "Parallelizable" field match the actual BLOCKS/DEPENDS ON? Are there dependencies on closed tasks?
- **Completion protocol accuracy** — Do completion protocols reference the correct downstream ticket IDs? Cross-check with actual BLOCKS shown in `bd show`.

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

After presenting the report, ask the user: "Found N defects. Fix all? [Y/n]"

If approved, execute all fixes. You MUST use parallel Agent subagents to apply fixes — group independent updates (e.g., different issues that don't depend on each other) into separate agents. Sequential fixes are only needed when one fix depends on another (e.g., `bd dep remove` before `bd close`). After all agents complete, re-run `bd blocked` and `bd ready` to verify the graph is healthy.

## Guidelines

- Be pedantic. Report everything, even LOW-severity issues.
- Never skip an issue — audit ALL open issues.
- For code verification, only spot-check the 2-3 most critical claims. Don't read every file.
- If the bead system has no open issues (`bd list --status=open` returns nothing), report "No open beads to audit" and exit.
- Use parallel agents to read multiple issues simultaneously for speed.
