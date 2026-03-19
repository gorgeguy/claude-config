# Python Project Setup Command

Set up a new Python project named `$ARGUMENTS` with modern tooling and best practices.

## Project Structure to Create
```
$ARGUMENTS/
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── pyproject.toml
├── src/
│   └── $ARGUMENTS/
│       ├── __init__.py
│       └── main.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

## Setup Steps

1. **Create project directory and navigate into it:**
   ```bash
   mkdir $ARGUMENTS && cd $ARGUMENTS
   ```

2. **Initialize git repository:**
   ```bash
   git init
   ```

3. **Create src package structure:**
   ```bash
   mkdir -p src/$ARGUMENTS tests
   touch src/$ARGUMENTS/__init__.py tests/__init__.py
   ```

4. **Create pyproject.toml with modern Python tooling:**
   - Use Python 3.11+ as minimum version
   - Configure uv for dependency management
   - Set up ruff for linting and formatting (replaces black, isort, flake8)
   - Configure pytest with coverage
   - Include build system configuration
   - Add common development dependencies

5. **Create .gitignore for Python projects:**
   - Include standard Python ignores (*.pyc, __pycache__, .env, etc.)
   - Add IDE-specific ignores (.vscode/, .idea/)
   - Include testing and build artifacts

6. **Set up .pre-commit-config.yaml:**
   - Configure ruff for linting and formatting
   - Add pytest to run tests before commits
   - Include common hooks (trailing whitespace, end-of-file-fixer)

7. **Create basic application files:**
   - `src/$ARGUMENTS/main.py` with a simple CLI entry point
   - `src/$ARGUMENTS/__init__.py` with version info
   - `tests/test_main.py` with basic test structure

8. **Create README.md:**
   - Project description placeholder
   - Installation instructions using uv
   - Usage examples
   - Development setup instructions
   - Testing and contributing guidelines

9. **Initialize Python environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

10. **Install and configure pre-commit:**
    ```bash
    uv tool install pre-commit
    pre-commit install
    pre-commit run --all-files
    ```

11. **Create initial commit:**
    ```bash
    git add .
    git commit -m "feat: initial project setup with uv, ruff, and pytest"
    ```

12. **Verify setup:**
    - Run `ruff check` to verify linting setup
    - Run `ruff format --check` to verify formatting setup
    - Run `pytest` to verify test setup
    - Run `python -m $ARGUMENTS` to verify package installation

## File Templates to Create

### pyproject.toml
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "$ARGUMENTS"
version = "0.1.0"
description = "A brief description of $ARGUMENTS"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
    "ruff>=0.1.0",
    "pre-commit>=3.0",
    "mypy>=1.0",
]

[project.scripts]
$ARGUMENTS = "$ARGUMENTS.main:main"

[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH"]
ignore = ["E501", "B008"]

[tool.ruff.format]
quote-style = "single"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers", "--cov=src", "--cov-report=term-missing"]

[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
warn_return_any = true
```

### .gitignore
```
__pycache__/
*.py[cod]
.Python
build/
dist/
*.egg-info/
.coverage
htmlcov/
.pytest_cache/
.env
.venv
venv/
.vscode/
.idea/
.DS_Store
.ruff_cache/
.mypy_cache/
```

### .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
```

### src/$ARGUMENTS/__init__.py
```python
"""$ARGUMENTS package."""
__version__ = "0.1.0"
```

### src/$ARGUMENTS/main.py
```python
"""Main module for $ARGUMENTS."""
import sys
import argparse

def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="$ARGUMENTS application")
    parser.add_argument("--version", action="version", version="$ARGUMENTS 0.1.0")
    args = parser.parse_args()
    
    print("Hello from $ARGUMENTS!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### tests/test_main.py
```python
"""Tests for main module."""
import pytest
from $ARGUMENTS.main import main

def test_main():
    """Test main function."""
    result = main()
    assert result == 0
```

### README.md
```markdown
# $ARGUMENTS

Description of $ARGUMENTS.

## Installation
```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Usage
```bash
python -m $ARGUMENTS
```

## Development
```bash
pytest              # Run tests
ruff check          # Lint
ruff format         # Format
```
```

## Success Criteria

After completion:
- Project has clean structure following Python packaging best practices
- All tools (ruff, pytest, pre-commit) are working correctly
- Package can be imported and run
- Tests pass
- Pre-commit hooks are installed and working
- Git repository is initialized with proper .gitignore

Ask for confirmation before proceeding with each major step, and provide helpful output about what was created and how to use it.
