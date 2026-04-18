---
description: Convert an implementation plan into self-contained Beads tickets optimized for `bd ready` parallel execution
argument-hint: "<path-to-implementation-plan>"
---

# Plan → Beads Tickets (Self-contained + Claimable + Parallel-safe + Self-correcting)

Read and analyze `$ARGUMENTS` and create Beads epics + tasks that are:
- Self-contained (no continuous plan reference required)
- Small enough for one focused Claude/Codex session
- Correctly dependency-linked so `bd ready` shows truly claimable work across multiple parallel terminals/worktrees
- Self-correcting: each completed ticket propagates implementation reality to downstream tickets

## Labels (required)
Create and apply to every issue:
1) Collection label (workstream): short kebab-case, derived from plan (2–4 words), e.g. `ws-<name>`
2) Execution label (unique per run): `run-YYYY-MM-DD-HHMM` (local time)

Also apply:
- Domain label(s): one of `domain-infra`, `domain-api`, `domain-data`, `domain-ui`, `domain-docs`, `domain-tests`, `domain-tooling`
- Optional: `blocked-external`

Before selecting labels, run `bd label list-all` and avoid collisions.

## Preflight (required)
Run:
- `bd list --status=open`
Do not create duplicates. If an equivalent issue exists, reuse it and do not recreate.

## Plan Analysis (required — do this BEFORE creating any tickets)
Before decomposing into tickets, write a brief synthesis of the plan covering:
- **Gaps & Ambiguities**: anything underspecified, contradictory, or missing that would block implementation
- **Key Design Decisions**: choices the plan makes (or defers) and their implications
- **Rationale & Intent**: the overarching goals this plan serves, why this approach was chosen over alternatives, and what "success" looks like beyond just completing tasks
- **Risks & Unknowns**: technical risk, integration risk, ordering risk, things that might change mid-execution
- **Recommendations**: any suggested reorderings, splits, or scope adjustments before ticketing

Include this synthesis as a comment or preamble in the output so that a future agent (or your future self) picking up this workstream cold understands not just *what* to build but *why* and *what to watch out for*.

If the analysis surfaces ambiguities that would produce low-quality tickets, stop and ask for clarification before proceeding to ticket creation.

## Parse plan → work graph
Extract:
- Epics (major sections)
- Tasks (implementable units)
- Hard dependencies (must be complete first)
- Soft dependencies (nice-to-have ordering; do NOT encode as blockers)
- External blockers (access, credentials, approvals, unknowns)
- Serialized/collision constraints ("exclusive locks"): schema/migrations, terraform/state, shared contracts, shared config

## External blockers (required)
For each external blocker, create a dedicated task issue:
- Title starts with `Blocker: ...`
- Label `blocked-external`
- Includes: what's needed, who/where, how to verify, and what becomes unblocked
All dependent tasks must hard-depend on the blocker issue via `bd dep add`.

## Parallel-safety: collision/lock chaining (required)
Detect tasks that should not be worked concurrently because they touch the same serialized resource.
For each lock group (examples: `db-migrations`, `terraform-state`, `api-contract`, `shared-config`):
- Choose the safest logical order (prefer earlier prerequisites first)
- Add hard deps to CHAIN them in sequence so only the first is ready at a time.
- Record the lock in each ticket under "Parallelism".

Goal: two `bd ready` tickets should not cause merge conflicts or conflicting state updates in shared resources.

## Ticket sizing rules (required)
Tickets must be sized so a single Claude Code session can implement them end-to-end.
Split if any of these are true:
- touches >3 subsystems OR >3 key files
- mixes design decisions + implementation in one step (split "spike/decision" first)
- unclear inputs (create a blocker/spike ticket)
- acceptance criteria would exceed ~6 checkboxes

Prefer more smaller tickets over fewer larger ones.

## Templates (must be self-contained)

### Epic (`bd create --type=epic`)
Include:
- Business Rationale
- Scope (in/out)
- Acceptance Criteria
- Risks / Open Questions
- Context Files (paths + purpose)
- Links/Traceability to plan sections

### Task / Feature / Bug
Each ticket MUST include:

**## Summary**
One paragraph. What changes.

**## Why**
Reason / user value.

**## Implementation Plan**
Concrete steps, in order.

**## Acceptance Criteria**
Checkboxes (testable).

**## Context Files**
List likely files to read/modify/create (with brief why).

**## Traceability**
Plan section(s) and requirement IDs.

**## Parallelism**
- Domain: one of the domain labels
- Parallelizable: yes/no
- Serialized resource (lock): `<name>` or `none`
- Notes on coordination if any

**## Dependencies**
- Hard deps: list (will be encoded via `bd dep add`)
- Soft deps: notes only (no blockers)

**## Completion Protocol**
When closing this ticket, the completing agent MUST:
1. **Record Actual Implementation**: what was built, key decisions made,
   any deviations from the implementation plan above and why.
   Add this as a closing comment on the ticket.
2. **Update downstream tickets** that hard-depend on this one:
   - Revise their Context Files if file paths or interfaces changed
   - Revise their Implementation Plan if assumptions were invalidated
   - Adjust Acceptance Criteria if scope shifted
   - Add new dependencies or blockers discovered during implementation
3. **Invalidation check**: if a downstream ticket is now obsolete or needs
   significant redesign, add a comment explaining what changed and why,
   and re-assign it to `needs-triage` status (or equivalent).
4. **Surface emergent work**: if implementation revealed necessary work
   not captured in any existing ticket, create new ticket(s) following
   this same template, with proper labels, deps, and lock-group chaining.

This protocol ensures the ticket graph is a living, self-correcting system —
each completed ticket makes remaining tickets *more* accurate, not less.

## Creation order (required)
1) Create epics
2) Create tasks and attach to epics if Beads supports it (otherwise reference epic in body)
3) Add ALL hard deps using `bd dep add` after IDs exist
4) Re-run `bd ready` and sanity-check that claimable tickets make sense

## Validation (required)
Report:
- Mapping coverage: every plan item → ticket (or "not ticketed" with reason)
- No duplicate tickets created
- Every ticket has: labels (collection + execution + domain), acceptance criteria, context files, traceability
- Every dependency from the plan is encoded as `bd dep add`
- Lock groups are chained (so concurrent terminals don't collide)
- Every task ticket includes a Completion Protocol section

## Phase 5: Fresh-eyes audit (required)

After all tickets are created, linked, and validated, run the `/audit-beads` process on the newly created issues. You MUST:

1. Spawn a fresh Agent (subagent_type=general-purpose) with NO context from earlier phases — this is the "fresh eyes" requirement
2. The agent should run `bd show <id>` for every issue created in this run (filter by the execution label)
3. The agent checks every issue against the `/audit-beads` checklist: stale references, description/notes consistency, epic coherence, dependency graph correctness, missing test plans, and completion protocol accuracy
4. For the 2-3 highest-severity issues, the agent should spot-check code claims (line numbers, function names, field types) against actual source files using Grep/Read
5. If defects are found, fix them immediately — do NOT ask the user. This is a self-healing step built into the creation process.
6. Report a summary: how many issues audited, how many defects found and fixed, how many are clean

This step catches false findings, stale references, and inaccurate code claims BEFORE the user starts implementing — preventing wasted work on tickets that reference nonexistent bugs or wrong line numbers.

## Output (required)
Print:
1) The chosen collection label and execution label
2) A compact list of created/reused issue IDs with title, domain, lock, and whether `bd ready` should show it now
3) Commands executed
4) `bd list -l <execution-label>`
5) `bd ready -l <collection-label>` (if supported) or plain `bd ready` with a note on how to filter
6) Audit results: defects found/fixed, clean count
