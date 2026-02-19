---
name: create-web-app
description: Scaffold full-stack project with Angular 21 and FastAPI backend
---

# Create Project

Scaffold a complete full-stack project with Angular 21 + Angular Material frontend and FastAPI Python backend.

## When to Use

- Starting a new full-stack project
- Setting up Angular 21 with Material Design
- Creating FastAPI backend with hello world endpoint
- Need development scripts (start services, run tests, lint)

## Interactive Setup

Before scaffolding, ask the user:

1. **Project name**: Used for folder names and package.json
2. **UI port**: Port for Angular dev server (e.g., 6444, 4467, 3000)
3. **API port**: Port for FastAPI backend (e.g., 6433, 8435)
4. **Worker needed?**: Whether the project needs a background worker process (default: yes)

## Project Structure Created

```
<project-root>/
├── .nvmrc                          # Node.js version for nvm (20.19)
├── src/
│   ├── ui/                          # Angular 21 frontend
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── core/            # Core module (interceptors, guards, services)
│   │   │   │   ├── shared/          # Shared module (components, directives, pipes)
│   │   │   │   ├── features/        # Feature modules
│   │   │   │   ├── app.component.ts
│   │   │   │   ├── app.component.html
│   │   │   │   ├── app.component.scss
│   │   │   │   └── app.routes.ts
│   │   │   ├── api-integration/     # Generated API services (from after_api_change.py)
│   │   │   └── ...
│   │   ├── tsconfig.json            # With path aliases
│   │   ├── proxy.conf.json          # API proxy config
│   │   └── package.json
│   ├── api/                         # FastAPI backend
│   │   ├── __init__.py
│   │   └── main.py                  # Hello world endpoint
│   ├── worker/                      # Background worker (optional)
│   │   ├── __init__.py
│   │   ├── main.py                  # Worker entry point with polling loop
│   │   ├── build_processor.py       # Build/task processor (stub)
│   │   └── deploy_processor.py      # Deploy/task processor (stub)
│   └── shared/                      # Shared code (used by both API and worker)
│       ├── __init__.py
│       ├── common.py                # Configuration and path utilities
│       ├── base_dto.py              # BaseDTO with camelCase conversion
│       ├── common_dto.py            # StatusDTO, ErrorDTO
│       ├── audit.py                 # File-based audit trail
│       ├── dtos/                    # DTOs (shared between API and worker)
│       │   └── __init__.py
│       ├── services/                # Business logic services
│       │   └── __init__.py
│       └── db/
│           ├── __init__.py
│           ├── db_context.py        # Database session manager
│           ├── models/              # SQLModel classes
│           │   └── __init__.py
│           ├── repositories/        # Data access layer
│           │   └── __init__.py
│           └── scripts/
│               ├── create_schema.sql
│               └── migrations/
├── after_api_change.py              # OpenAPI to TypeScript generator
├── start_services.py                # Service orchestrator (API + UI + Worker)
├── setup_db.py                      # Database setup script
├── run_tests.py                     # Test runner
├── lint.py                          # Linting tool
├── utils.py                         # Shared utilities
└── pyproject.toml                   # Python dependencies (uv managed)
```

## Instructions

### 1. Ask for Configuration

Ask user for project name, ports, and whether they need a worker before proceeding.

### 2. Create .nvmrc File

Create `.nvmrc` in the project root with content `20.19` to specify the Node.js version for nvm.

### 3. Create Angular Frontend

Follow `references/angular-setup.md` to:

- Initialize Angular 21 project with Angular Material
- Set up folder structure (core, shared, features)
- Configure tsconfig path aliases
- Create HTTP interceptor
- Set up proxy configuration

### 4. Create FastAPI Backend

Follow `references/fastapi-setup.md` to:

- Create minimal FastAPI application
- Add hello world endpoint
- Configure CORS for Angular dev server

### 5. Create Worker (if needed)

Follow `references/worker-setup.md` to:

- Create worker entry point with polling loop
- Set up signal handling for graceful shutdown
- Create stub processor files
- Configure database polling interval

### 6. Create Development Scripts

Follow `references/scripts-setup.md` to:

- Create start_services.py orchestrator (includes worker if applicable)
- Create run_tests.py test runner
- Create lint.py formatting tool
- Create utils.py shared logger

### 7. Create API Code Generator

Follow `references/after-api-change-setup.md` to:

- Create after_api_change.py script
- Configure API port for OpenAPI URL
- Create api-integration directory structure

### 8. Create pyproject.toml

Follow `references/pyproject-setup.md` to:

- Create uv-managed pyproject.toml
- Add FastAPI, uvicorn, and dev dependencies

### 9. Initialize Project

```bash
# Use correct Node.js version (if using nvm)
nvm use

# Install Angular dependencies
cd src/ui && npm install

# Initialize Python environment with uv
uv sync

# Verify setup
uv run python start_services.py
```

## Key Configuration

### TypeScript Path Aliases

```json
{
  "paths": {
    "@core/*": ["src/app/core/*"],
    "@shared/*": ["src/app/shared/*"],
    "@features/*": ["src/app/features/*"]
  }
}
```

### Proxy Configuration

Proxy `/api` requests to FastAPI backend during development.

### HTTP Interceptor

Basic interceptor that:

- Adds authentication headers to API requests
- Handles 401 responses

## Shared Code Architecture

Services and DTOs live in `src/shared/` (NOT in `src/api/`) because both the API and worker need access to business logic:

- `src/shared/base_dto.py` - BaseDTO with camelCase conversion
- `src/shared/common_dto.py` - StatusDTO, ErrorDTO
- `src/shared/dtos/` - Feature-specific DTOs
- `src/shared/services/` - Business logic services
- `src/api/` - Only routers, middleware, and dependency injection
- `src/worker/` - Only worker-specific processing logic

## Worker Architecture

The worker uses **database polling** as its queuing mechanism:

1. API writes records with `status = "pending"` to the database
2. Worker polls the database every N seconds for pending work
3. Worker processes one task at a time (sequential by default)
4. Worker marks tasks as `"ongoing"` while processing, `"completed"` or `"failed"` when done
5. On startup, worker recovers stale tasks (marks any `"ongoing"` tasks as `"failed"`)

### Queuing Guarantees

- **One build at a time**: Worker picks only one pending build per poll cycle
- **One deployment per environment**: Worker checks for ongoing deployments to the same environment before starting a new one
- **FIFO ordering**: Pending tasks are ordered by `created_at` timestamp
- **Crash recovery**: On startup, any `ongoing` tasks are marked as `failed`

This pattern uses SQLite as the queue. No external message broker needed.

## Templates

See reference files for detailed templates:

- `references/angular-setup.md` - Angular scaffolding
- `references/fastapi-setup.md` - FastAPI setup
- `references/worker-setup.md` - Worker polling loop setup
- `references/scripts-setup.md` - Python development scripts
- `references/pyproject-setup.md` - Python project configuration
- `references/after-api-change-setup.md` - OpenAPI to TypeScript generator

