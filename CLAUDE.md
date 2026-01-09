# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Install dependencies (in virtual environment)
pip install -e .               # Install package in editable mode
pip install -r requirements.txt # Install dev dependencies (pytest, black, isort, etc.)

# Run all tests
pytest

# Run single test file
pytest tests/test_cli.py

# Run specific test
pytest tests/test_cli.py::test_list_documents

# Run tests with coverage
pytest --cov=omnifact_cli

# Format code
black omnifact_cli tests
isort omnifact_cli tests
```

## Architecture

This is a Python CLI application built with Click that interacts with the Omnifact API for document management and chat functionality.

### Key Components

- **`omnifact_cli/cli.py`**: Click command definitions and entry point (`omnifact-cli`). Defines all CLI commands as decorated functions using `@cli.command()`.

- **`omnifact_cli/api.py`**: `OmnifactAPI` class that wraps all HTTP calls to the Omnifact Connect API. Uses `requests.Session` for connection reuse with API key authentication via `X-API-Key` header.

- **`omnifact_cli/config.py`**: Configuration management. Reads/writes to `~/.omnifact_cli.ini`. Environment variables `OMNIFACT_API_KEY` and `OMNIFACT_CONNECT_URL` take precedence over config file values.

### API Endpoints Used

All API calls go to the Omnifact Connect API (default: `https://connect.omnifact.ai`):
- Documents: `/v1/documents` (CRUD operations)
- Chat: `/v1/endpoints/{endpoint_id}/chat` (SSE streaming)

### Testing Pattern

Tests use Click's `CliRunner` for CLI testing and `unittest.mock.patch` to mock:
- `omnifact_cli.cli.get_api_key` - to bypass API key requirement
- `omnifact_cli.api.OmnifactAPI.*` - to mock API responses
