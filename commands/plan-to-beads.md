---
description: Convert an implementation plan into self-contained Beads tickets optimized for `bd ready` parallel execution
argument-hint: "<path-to-implementation-plan>"
---

# Plan → Beads Tickets (Self-contained + Claimable + Parallel-safe)

Read and analyze `$ARGUMENTS` and create Beads epics + tasks that are:
- Self-contained (no continuous plan reference required)
- Small enough for one focused Claude/Codex session
- Correctly dependency-linked so `bd ready` shows truly claimable work across multiple parallel terminals/worktrees

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

## Parse plan → work graph
Extract:
- Epics (major sections)
- Tasks (implementable units)
- Hard dependencies (must be complete first)
- Soft dependencies (nice-to-have ordering; do NOT encode as blockers)
- External blockers (access, credentials, approvals, unknowns)
- Serialized/collision constraints (“exclusive locks”): schema/migrations, terraform/state, shared contracts, shared config

## External blockers (required)
For each external blocker, create a dedicated task issue:
- Title starts with `Blocker: ...`
- Label `blocked-external`
- Includes: what’s needed, who/where, how to verify, and what becomes unblocked
All dependent tasks must hard-depend on the blocker issue via `bd dep add`.

## Parallel-safety: collision/lock chaining (required)
Detect tasks that should not be worked concurrently because they touch the same serialized resource.
For each lock group (examples: `db-migrations`, `terraform-state`, `api-contract`, `shared-config`):
- Choose the safest logical order (prefer earlier prerequisites first)
- Add hard deps to CHAIN them in sequence so only the first is ready at a time.
- Record the lock in each ticket under “Parallelism”.

Goal: two `bd ready` tickets should not cause merge conflicts or conflicting state updates in shared resources.

## Ticket sizing rules (required)
Tickets must be sized so a single Claude Code session can implement them end-to-end.
Split if any of these are true:
- touches >3 subsystems OR >3 key files
- mixes design decisions + implementation in one step (split “spike/decision” first)
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

## Creation order (required)
1) Create epics
2) Create tasks and attach to epics if Beads supports it (otherwise reference epic in body)
3) Add ALL hard deps using `bd dep add` after IDs exist
4) Re-run `bd ready` and sanity-check that claimable tickets make sense

## Validation (required)
Report:
- Mapping coverage: every plan item → ticket (or “not ticketed” with reason)
- No duplicate tickets created
- Every ticket has: labels (collection + execution + domain), acceptance criteria, context files, traceability
- Every dependency from the plan is encoded as `bd dep add`
- Lock groups are chained (so concurrent terminals don’t collide)

## Output (required)
Print:
1) The chosen collection label and execution label
2) A compact list of created/reused issue IDs with title, domain, lock, and whether `bd ready` should show it now
3) Commands executed
4) `bd list -l <execution-label>`
5) `bd ready -l <collection-label>` (if supported) or plain `bd ready` with a note on how to filter
