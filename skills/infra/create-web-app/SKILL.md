---
name: create-web-app
description: |
  Scaffold a new full-stack project with Angular 20 frontend and FastAPI backend.
  Use when: Starting a new project from scratch, setting up a new application with
  Angular Material UI and Python API backend with development scripts.
---

# Create Project

Scaffold a complete full-stack project with Angular 20 + Angular Material frontend and FastAPI Python backend.

## When to Use

- Starting a new full-stack project
- Setting up Angular 20 with Material Design
- Creating FastAPI backend with hello world endpoint
- Need development scripts (start services, run tests, lint)

## Interactive Setup

Before scaffolding, ask the user:

1. **Project name**: Used for folder names and package.json
2. **UI port**: Port for Angular dev server (e.g., 6444, 4467, 3000)
3. **API port**: Port for FastAPI backend (e.g., 6433, 8435)

## Project Structure Created

```
<project-root>/
├── .nvmrc                          # Node.js version for nvm (20.19)
├── src/
│   ├── ui/                          # Angular 20 frontend
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
│   └── api/                         # FastAPI backend
│       ├── __init__.py
│       └── main.py                  # Hello world endpoint
├── after_api_change.py              # OpenAPI to TypeScript generator
├── start_services.py                # Service orchestrator
├── run_tests.py                     # Test runner
├── lint.py                          # Linting tool
├── utils.py                         # Shared utilities
└── pyproject.toml                   # Python dependencies (uv managed)
```

## Instructions

### 1. Ask for Configuration

Ask user for project name and ports before proceeding.

### 2. Create .nvmrc File

Create `.nvmrc` in the project root with content `20.19` to specify the Node.js version for nvm.

### 3. Create Angular Frontend

Follow `references/angular-setup.md` to:

- Initialize Angular 20 project with Angular Material
- Set up folder structure (core, shared, features)
- Configure tsconfig path aliases
- Create HTTP interceptor
- Set up proxy configuration

### 4. Create FastAPI Backend

Follow `references/fastapi-setup.md` to:

- Create minimal FastAPI application
- Add hello world endpoint
- Configure CORS for Angular dev server

### 5. Create Development Scripts

Follow `references/scripts-setup.md` to:

- Create start_services.py orchestrator
- Create run_tests.py test runner
- Create lint.py formatting tool
- Create utils.py shared logger

### 6. Create API Code Generator

Follow `references/after-api-change-setup.md` to:

- Create after_api_change.py script
- Configure API port for OpenAPI URL
- Create api-integration directory structure

### 7. Create pyproject.toml

Follow `references/pyproject-setup.md` to:

- Create uv-managed pyproject.toml
- Add FastAPI, uvicorn, and dev dependencies

### 8. Initialize Project

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

## Templates

See reference files for detailed templates:

- `references/angular-setup.md` - Angular scaffolding
- `references/fastapi-setup.md` - FastAPI setup
- `references/scripts-setup.md` - Python development scripts
- `references/pyproject-setup.md` - Python project configuration
- `references/after-api-change-setup.md` - OpenAPI to TypeScript generator
