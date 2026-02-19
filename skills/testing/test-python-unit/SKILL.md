---
name: test-python-unit
description: |
---

# Backend Test Creation

Create pytest unit tests for backend functionality following project testing patterns.

## When to Use

- Writing tests after implementing services, repositories, or routers
- Adding test coverage to existing backend code
- Testing error scenarios, edge cases, and validation logic

## File Structure

Tests mirror `src/` structure with one folder per source file and one test file per method:

```
src/tests/
├── api/
│   └── services/
│       └── <service_name>/           # Unit tests (with mocking)
│           ├── test_<method>.py
│           └── conftest.py
├── shared/
│   └── db/repositories/
│       └── <domain>_repository/
│           └── <table>_repository/
│               ├── test_<method>.py
│               └── conftest.py
└── conftest.py                  # Global fixtures
```

## Test Types

### Service/Router Unit Tests
- **Use mocking** for dependencies (MagicMock, patch)
- **Test all scenarios**: happy path, edge cases, error handling
- **Use `db_session` fixture** which auto-rollbacks changes
- Located in `<service_name>/` folder

### Repository Tests
- **Use real database** via `db_session` fixture
- **Test CRUD operations** and query methods
- **Auto-rollback** ensures isolation between tests
- Located in `<domain>_repository/<table>_repository/` folder

## Instructions

### 1. Create Test File

Create ONE test file at a time, following the naming pattern.

### 2. Run Test Immediately

```bash
uv run pytest src/tests/path/to/test_file.py -v
```

### 3. Verify Zero Warnings

Fix any warnings before proceeding to next test.

### 4. Repeat

Only then create the next test file.

## Key Rules

1. **One folder per source file**: Each source file gets its own test folder
2. **One test file per method**: Each method gets its own test file
3. **Module-level functions only**: No class wrappers - use pytest functions
4. **Mirror structure**: Test folders mirror `src/` exactly
5. **Test immediately**: Create ONE file, run, validate, then proceed
6. **Zero warnings**: All tests must pass with zero warnings
7. **AAA pattern**: Arrange, Act, Assert structure

## Database Lifecycle

- Database created **ONCE per pytest-xdist worker** via `setup_db.py`
- Unit tests: rollback changes at end (via `db_session` fixture)
- Never recreate DB per test - too slow

## Shared Fixtures (conftest.py)

Create reusable `conftest.py` files to minimize repetition:

```
src/tests/
├── conftest.py                      # Global fixtures (db_session, etc.)
├── api/
│   └── services/
│       └── auth_service/
│           └── conftest.py          # Shared fixtures for auth_service unit tests
```

### Local conftest.py Example

```python
"""Shared fixtures for auth_service unit tests."""

import pytest
from unittest.mock import MagicMock

from api.services.auth_service import AuthService


@pytest.fixture
def mock_db():
    """Create mock database session."""
    return MagicMock()


@pytest.fixture
def auth_service(mock_db):
    """Create AuthService with mocked db."""
    return AuthService(mock_db)
```

Then tests can simply use the fixture:

```python
def test_login_success(auth_service):
    """Test uses shared auth_service fixture."""
    # auth_service is already set up with mock db
    ...
```

## Running Tests

```bash
# Run single test file
uv run pytest src/tests/path/to/test_file.py -v

# Run Python tests
uv run run_tests.py python

# Run with coverage
uv run run_tests.py python -cv

# Run quality checks
uv run run_tests.py quality
```

## Templates

See `references/` folder for:

- `unit-test-patterns.md` - Unit test examples for services, repos, routers


