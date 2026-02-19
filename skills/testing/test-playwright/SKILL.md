---
name: test-playwright
description: Create Playwright E2E tests using Page Object pattern for user workflows
---

# E2E Test Creation

Create Playwright E2E tests using the Page Object pattern for maintainability and reusability.

## When to Use

- Testing complete user workflows (login, CRUD operations, navigation)
- Validating UI interactions across multiple pages
- Testing form submissions and validation
- Verifying authentication and authorization flows

## Prerequisites

1. Feature fully implemented and manually tested
2. Angular frontend running on configured port
3. Backend API running

## Directory Structure

```
src/tests/e2e/
├── conftest.py                    # Pytest fixtures
├── pages/                         # Page objects
│   ├── base_page.py              # Base class for all pages
│   ├── auth_utils.py             # Authentication utilities
│   └── <feature>/                # Feature-specific pages
│       └── <feature>_page.py
├── tests/                        # Test files
│   └── <feature>/
│       └── test_<scenario>.py
└── utils/                        # Utilities
    ├── test_paths.py             # URL path constants
    ├── page_utils.py             # Page utilities
    └── screenshot_on_failure.py  # Artifact capture
```

## Instructions

### 1. Create Base Infrastructure (first time only)

If this is a fresh project, create the base infrastructure following `references/base-infrastructure.md`:
- `base_page.py` - Base class with common methods
- `conftest.py` - Pytest fixtures for browser, database
- `screenshot_on_failure.py` - Artifact capture utilities

### 2. Create Page Object

Create page object class extending `BasePage` with selectors and methods.

### 3. Create Test File

Create async test using page objects with artifact capture.

### 4. Run Tests

```bash
# Run specific test
uv run pytest src/tests/e2e/tests/<feature>/test_<scenario>.py -v

# Run all e2e tests
uv run pytest src/tests/e2e/ -v -m e2e

# Run with visible browser (debug)
uv run pytest src/tests/e2e/ -v --headed
```

## Key Rules

1. **Page Object pattern**: One class per page/section with all selectors as instance variables
2. **Async/await**: All methods must be async (Playwright requirement)
3. **data-test-id selectors**: Primary selector strategy for decoupling from CSS
4. **Wait after actions**: Always wait for navigation/state changes after clicks
5. **Business-level methods**: Page objects expose high-level actions, not raw Playwright calls
6. **Artifact capture**: Use `run_with_screenshot_on_failure` wrapper for debugging
7. **Database fixtures**: Use repositories to set up test data, not API calls

## Templates

See `references/` folder for:
- `base-infrastructure.md` - Base page class, conftest fixtures, utilities
- `page-object-template.md` - Page object class patterns
- `test-template.md` - Test file structure and patterns


