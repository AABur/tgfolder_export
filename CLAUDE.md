# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

```bash
# Install uv if not already installed: https://docs.astral.sh/uv/getting-started/installation/
make init           # Set up virtual environment, install dependencies, create directories
source .venv/bin/activate  # Activate virtual environment
```

## Configuration Required

Before running the application, create `var/config.yml`:
```yaml
tg:
  app_id: ...      # Telegram app ID
  app_hash: ...    # Telegram app hash
```

## Common Commands

```bash
# Run the exporter
./export.py > export.json

# Testing
make test          # Run pytest tests
make test-cov      # Run tests with coverage report

# Code quality checks
make check          # Run all linting, type checking, and tests
make ruff          # Run ruff linter and formatter
make mypy          # Run mypy type checker

# Individual linting tools
uv run ruff check export.py
uv run ruff format export.py
uv run mypy export.py

# Build package
make build

# Clean up
make clean
```

## Architecture

This is a single-file Python script that exports Telegram folder contents using the Telethon library. The main components:

- **Configuration**: Loads Telegram API credentials from `var/config.yml`
- **Entity Processing**: Functions to extract and format channel/group information (`get_entity_type_name`, `get_entity_name`, `export_entity`)
- **Dialog Filter Export**: Main logic in `export_dialog_filter` that processes each Telegram folder and extracts peer information
- **Error Handling**: Handles `ChannelPrivateError` for inaccessible channels
- **Output**: JSON serialization of folder structure with channel/group metadata

The script processes Telegram dialog filters (folders), extracts included peers (channels/groups), and outputs structured JSON data with entity type, ID, username, and name information.

## Code Style Guidelines

- Uses type hints throughout (Python 3.11+ syntax)
- Line length: 88 characters (Black/Ruff standard)
- Extensive linting configuration in `pyproject.toml`
- Follows strict mypy type checking
- Maintain test coverage at 85% or higher
- Error handling: check errors immediately and return them with context
- Use meaningful variable names; avoid single-letter names except in loops
- Validate function parameters at the start before processing
- Return early when possible to avoid deep nesting
- Function size preferences:
  - Aim for functions around 50-60 lines when possible
  - Don't break down functions too small as it can reduce readability
  - Maintain focus on a single responsibility per function
- Code width: keep lines under 130 characters when possible

## Important Workflow Notes

- Always run tests and linter BEFORE committing anything
- Run tests and linter after making significant changes to verify functionality
- Don't add "Generated with Claude Code" or "Co-Authored-By: Claude" to commit messages or PRs
- Do not include "Test plan" sections in PR descriptions
- Do not add comments that describe changes, progress, or historical modifications
- Avoid comments like "new function," "added test," "now we changed this," or "previously used X, now using Y"
- Comments should only describe the current state and purpose of the code, not its history or evolution
- After important functionality added, update README.md accordingly
- When merging master changes to an active branch, make sure both branches are pulled and up to date first

## Testing

- Uses pytest with pytest-mock for modern testing approach
- Target test coverage: 85% minimum
- Don't create too large tests if they are complicated, but split them into multiple tests
- Keep tests compact but readable
- Never disable tests without a good reason. If you have a good reason, ask for approval first and if accepted, disable them with a comment explaining the reason
- Never update code with special conditions to just pass tests
- **Never change tests and code simultaneously! When fixing errors in tests, fix ONLY tests!**
- Use `mocker` fixture from pytest-mock instead of unittest.mock for better pytest integration