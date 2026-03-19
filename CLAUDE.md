# CLAUDE.md - Global Python Development Configuration

This document contains critical information about working with
all python projects. Follow these guidelines precisely.

## Core Development Rules

1. Package Management
   - ONLY use uv, NEVER pip
   - Installation: `uv add package`
   - Running tools: `uv run tool`
   - Upgrading: `uv add --dev package --upgrade-package package`
   - FORBIDDEN: `uv pip install`, `@latest` syntax

2. Code Quality
   - Public APIs must have docstrings
   - Functions must be focused and small
   - Follow existing patterns exactly

3. Testing Requirements
   - Framework: `uv run --frozen pytest`
   - Async testing: use anyio, not asyncio
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests
   - Use descriptive test function names: `test_should_return_user_when_valid_id_provided`
   - Include docstrings for complex functions and classes

## Code Style & Standards
- Follow PEP 8 for code style
- Import order: standard library, third-party, local imports
- Use type hints for all function parameters and return values
- Line length: 100 chars maximum
- Prefer f-strings over .format() or % formatting
- Use pathlib.Path instead of os.path for file operations

## Code Formatting

1. Ruff
   - Format: `uv run --frozen ruff format .`
   - Check: `uv run --frozen ruff check .`
   - Fix: `uv run --frozen ruff check . --fix`
   - Critical issues:
     - Line length (100 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. Type Checking
   - Tool: `uv run --frozen pyright`
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass

3. Pre-commit
   - Config: `.pre-commit-config.yaml`
   - Runs: on git commit
   - Tools: Prettier (YAML/JSON), Ruff (Python)
   - Ruff updates:
     - Check PyPI versions
     - Update config rev
     - Commit config first

## Testing & Quality
- Use pytest as the default testing framework
- Test files should be named `test_*.py` or `*_test.py`
- Run tests before committing: `uv run --frozen pytest -v`
- Use coverage reporting: `pytest --cov=src`

## Project Structure Conventions
- Source code in `src/` directory when possible
- Tests in `tests/` directory mirroring src structure
- Configuration files in project root
- Use `__init__.py` files even if empty (for clarity)
- Keep related functionality in modules, not single large files

## Error Handling & Logging
- Use structured logging with the `logging` module
- Prefer specific exception types over bare `except:`
- Use context managers (`with` statements) for resource management
- Always handle exceptions at appropriate levels
- Use logging levels appropriately: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Dependencies & Security
- Pin exact versions in production requirements
- Use `uv` for dependency management
- Use .env files for environment variables, never hardcode secrets
- Validate input data with libraries like Pydantic when appropriate

## Git Workflow Integration
- Run linting and formatting before commits
- Use conventional commit messages: `feat:`, `fix:`, `docs:`, `refactor:`
- Create feature branches: `feature/descriptive-name`
- Ensure tests pass before merging
- Always merge, never rebase

## Performance & Best Practices
- Use list comprehensions over map/filter when readable
- Prefer `pathlib.Path` over string manipulation for file paths
- Use `dataclasses` or `Pydantic` models for structured data
- Consider `asyncio` for I/O-bound operations
- Profile before optimizing: use `cProfile` or `py-spy`

## Agent Autonomy
- Do NOT ask for confirmation between steps when executing a task. Work autonomously until the task is complete or you hit a genuine blocker.

## AI Collaboration Guidelines
- IMPORTANT: Always run tests after making changes
- Ask me to update this CLAUDE.md when you learn new project patterns
- Explain complex algorithms in comments and docstrings
- Use meaningful variable names: `user_count` not `n`
- Break large functions into smaller, testable pieces
- YOU MUST validate that code changes don't break existing functionality

## Personal Preferences
- Prefer explicit over implicit (Zen of Python)
- Use early returns to reduce nesting
- Keep functions under 50 lines when possible
- Add TODO comments for known technical debt
- Document why, not just what, in complex code sections
- Always use frontend-design when new frontend design needs to be performed.
- Do not run python-related tests when not making any changes to python code

## Port Management

IMPORTANT: Always use the `pm` CLI for port allocation. Never hardcode port numbers.

- **Project name**: Use the top 2 directory levels of the git repo (e.g., `gorgeguy/pbtourney` for `/Users/jon/g/gorgeguy/pbtourney`)
  - Derive with: `git rev-parse --show-toplevel | rev | cut -d/ -f1-2 | rev`
- **Workflow**: Query first, allocate if missing, then use the returned port
- **Port names**: `serve` (dev server), `web` (frontend), `api` (backend), `db` (database), `cache` (redis)
- **Port types** for allocation: `web` (8000-8999), `api` (3000-3999), `db` (5400-5499), `cache` (6300-6399)

Example:
  PROJECT=$(git rev-parse --show-toplevel | rev | cut -d/ -f1-2 | rev)
  PORT=$(pm query "$PROJECT" serve 2>/dev/null || pm allocate "$PROJECT" serve | grep -oE '[0-9]+')

