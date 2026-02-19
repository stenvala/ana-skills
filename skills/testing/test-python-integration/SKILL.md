---
name: test-python-integration
description: Create pytest integration tests for complete API workflow validation
---

# Integration Test Creation

Create pytest integration tests that test complete user workflows via FastAPI TestClient.

## When to Use

- **Only when explicitly requested by the user**
- Testing end-to-end API flows that span multiple endpoints
- Verifying complete user workflows work correctly
- Testing features that require multiple services to coordinate

## What Integration Tests Are

Integration tests exercise the **complete stack** through API endpoints:

1. **Use TestClient** - make real HTTP requests to endpoints
2. **Use real database** - no mocking, actual data persistence
3. **Test happy-day flows** - no error case testing (that's for unit tests)
4. **Use `accounting_prerequisites`** fixture for common setup
5. **Session-scoped fixtures** - reuse setup across tests in same worker

## File Structure

```
src/tests/integration/
├── conftest.py                           # Shared fixtures (auth_headers, accounting_prerequisites)
├── <feature_name>/
│   ├── conftest.py                       # Feature-specific fixtures
│   └── test_<workflow_description>.py    # One file per workflow
```

## Key Fixtures

### `test_client` (from root conftest.py)
FastAPI TestClient with test domain header set.

### `auth_headers` (from integration conftest.py)
```python
@pytest.fixture(scope="session")
def auth_headers(test_client: "TestClient") -> dict[str, str]:
    """Login as admin and return authorization headers."""
```

### `accounting_prerequisites` (from integration conftest.py)
```python
@pytest.fixture(scope="session")
def accounting_prerequisites(...) -> AccountingPrerequisites:
    """Create workflow stage, dimension type, fiscal year, bank account."""
```

## Test Pattern

```python
"""Integration test for [feature description].

Tests that [what the test verifies end-to-end].
"""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.integration.conftest import AccountingPrerequisites

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def test_<descriptive_name>(
    test_client: "TestClient",
    auth_headers: dict[str, str],
    accounting_prerequisites: AccountingPrerequisites,
) -> None:
    """[Describe what this test verifies].

    Setup:
    1. [What prerequisite data needs to be created]

    Test:
    1. [What API calls are made]
    2. [What is verified]
    """
    # 1. Setup - create any test-specific data via API
    response = test_client.post(
        "/api/private/some-endpoint",
        json={"field": "value"},
        headers=auth_headers,
    )
    assert response.status_code == 201

    # 2. Act - perform the main action being tested
    result = test_client.post(
        "/api/private/action-endpoint",
        json={"data": "..."},
        headers=auth_headers,
    )
    assert result.status_code == 200

    # 3. Assert - verify the complete workflow worked
    verify_response = test_client.get(
        "/api/private/verify-endpoint",
        headers=auth_headers,
    )
    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data["expected_field"] == "expected_value"
```

## Key Rules

1. **Only happy-day scenarios** - error testing belongs in unit tests
2. **Test via endpoints** - never call services directly
3. **Use auth_headers** - all private endpoints need authentication
4. **Session-scoped prerequisites** - reuse accounting_prerequisites across tests
5. **Descriptive test names** - describe the workflow being tested
6. **Document setup and test steps** - clear docstrings explaining the flow
7. **One workflow per file** - keep tests focused

## What NOT to Test

Integration tests verify the **system works correctly end-to-end**. Do NOT test:

- Invalid input handling (unit tests)
- Authentication failures (unit tests)
- Authorization failures (unit tests)
- Database constraint violations (unit tests)
- Edge cases and error scenarios (unit tests)

## Running Tests

```bash
# Run all integration tests
uv run pytest src/tests/integration/ -v -m integration

# Run specific integration test
uv run pytest src/tests/integration/feature/test_workflow.py -v
```

## Creating Feature-Specific Fixtures

For tests that need additional setup beyond `accounting_prerequisites`:

```python
# src/tests/integration/my_feature/conftest.py
"""Fixtures for my_feature integration tests."""

from pathlib import Path
import pytest

@pytest.fixture
def csv_file_path(tmp_path: Path) -> Path:
    """Create test CSV file for import testing."""
    csv_content = """header1,header2
value1,value2"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return csv_file
```

## Templates

See `references/` folder for:

- `integration-test-example.py` - Complete integration test example
