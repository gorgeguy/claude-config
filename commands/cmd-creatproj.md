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
   uv pip install -e ".[dev]"
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

## Additional Configuration

- Configure ruff to be compatible with pytest
- Set line length to 88 (Black-compatible)
- Enable modern Python features and type checking rules
- Set up pytest with coverage reporting and proper test discovery
- Include common development dependencies: pytest-cov, pytest-mock, pre-commit

## Success Criteria

After completion:
- Project has clean structure following Python packaging best practices
- All tools (ruff, pytest, pre-commit) are working correctly
- Package can be imported and run
- Tests pass
- Pre-commit hooks are installed and working
- Git repository is initialized with proper .gitignore

Ask for confirmation before proceeding with each major step, and provide helpful output about what was created and how to use it.
