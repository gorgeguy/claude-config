# Claude Global Configuration

This document contains global instructions loaded into every conversation.
Universal rules apply always; language-specific sections apply only when
that language is present in the project.

## Git Workflow

- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`
- Always merge, never rebase
- Each agent works in its own worktree — the worktree containing its current
  directory. Work on whatever branch that worktree has checked out; do not
  create or switch branches unless asked.
- Run linting, formatting, and the relevant tests before committing or
  merging. Do not run a language's test suite when you haven't changed that
  language's code.

## Agent Autonomy

- Do NOT ask for confirmation between steps when executing a task. Work
  autonomously until the task is complete or you hit a genuine blocker.

## Task Tracking & Memory

- Use beads (`bd`) for task tracking wherever a beads workspace exists — not
  TodoWrite/TaskCreate, even if the harness suggests them.
- Use `bd remember` for durable insights; it is shared across agents.

## Preferences

- Document why, not just what — explain non-obvious algorithms and
  constraints in docstrings or comments.
- Always use frontend-design when new frontend design needs to be performed.

## Durable References in Committed Artifacts

Commits, code comments, docstrings, and maintained docs are read by people
who don't share our session context: future you, other engineers/agents,
and reviewers without access to your local trackers or environments. Keep
references in committed artifacts to things that will still make sense to
that reader.

- **No Bead ticket IDs in commit messages, code, or docs.**
  Treat beads as ephemeral as we don't share beads with other people.
  Describe the bug or behavior in terms a reader can verify from
  the code itself.
- **No agent or session references.** Phrases like "as Codex flagged",
  "per our review", or "based on the previous conversation" don't survive
  context loss. State the observation directly.
- **No local environment names.** Test-env hostnames, personal worktree
  paths, sibling-repo aliases, customer-internal nicknames, and unreleased
  internal tooling names tie the doc to one person's setup.
- **Code references are durable; use them.** File paths, function/class/
  symbol names, and module identifiers live in the codebase the reader is
  looking at — prefer "see `_filter_already_processed`" over "see
  ticket #1234".
- **External stable references are fine.** RFCs, vendor docs at stable
  URLs, and standards body specs.

If context doesn't fit these rules but you need to preserve it, put it in
the PR description (different audience, different lifecycle), not in the
committed artifact.

## When Working in Python Projects

Apply these rules when the project contains Python code (pyproject.toml,
*.py files, etc.).

### Project Template

When creating a new Python project, use
**[gorgeguy/python-template](https://github.com/gorgeguy/python-template)**
(local: `~/g/gorgeguy/python-template`) as the starting point — copy it
rather than starting from scratch. It includes pre-configured ruff rules,
pyright, pre-commit hooks, GitHub Actions CI, Makefile, VS Code settings,
and a CLAUDE.md with agent instructions. The template's ruff/pyright config
is the style authority (line length, import order, quoting, f-strings) —
rely on the linters rather than restating style rules.

### Package Management

- ONLY use uv, NEVER pip
- Installation: `uv add package`; running tools: `uv run tool`;
  upgrading: `uv add --dev package --upgrade-package package`
- FORBIDDEN: `uv pip install`, `@latest` syntax

### Testing

- Framework: `uv run --frozen pytest`; async testing uses anyio, not asyncio
- New features require tests; bug fixes require regression tests; cover
  edge cases and errors
- Descriptive test names (`test_should_return_user_when_valid_id_provided`);
  test files live in `tests/` and are named `test_*.py`

### Quality Gates

- Format: `uv run --frozen ruff format .` — Lint: `uv run --frozen ruff
  check . --fix` — Types: `uv run --frozen pyright`
- Public APIs must have docstrings; use type hints on function signatures
- Use `.env` files for secrets; never hardcode them
