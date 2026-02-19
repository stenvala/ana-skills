---
name: database-setup-sqlite
description: |
---

# Setup SQLite Database

Create an SQLite database with setup script, schema initialization, and migration support.

## When to Use

- Setting up a new SQLite database for local development
- Need file-based database
- Projects requiring migration support
- Simple applications without PostgreSQL dependency

## Tenancy Modes

This skill supports two modes:

### Single-Tenant (default)

- Database at `mcc/data/data.db`
- Simpler code: no domain parameter needed
- Use `get_data_dir()` for path resolution

### Multitenant

- Database per domain at `mcc/domains/<domain>/data.db`
- Use `--domain` flag on setup_db.py commands
- Use `get_directory_for_domain(domain)` for path resolution
- Use `DBContext(domain)` for domain-specific sessions

Choose based on project requirements. If in doubt, use single-tenant.

## Instructions

### 1. Create Directory Structure

Create the database scripts directory:

```
src/
└── shared/
    ├── common.py                 # Shared utilities
    └── db/
        ├── __init__.py
        ├── db_context.py         # Database session manager
        └── scripts/
            ├── create_schema.sql  # Initial schema (with migrations table)
            ├── demo_data.sql      # Optional demo data
            └── migrations/        # Migration files
                └── 001_example.sql
```

### 2. Create setup_db.py

Create the setup script from `references/sqlite-setup.md` template in the project root. Choose the single-tenant or multitenant template based on project needs.

### 3. Create Schema File

Create `src/shared/db/scripts/create_schema.sql`. Always include the migrations table:

```sql
-- Migrations tracking table (required)
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add your tables below
```

### 4. Create Common Utilities

Create `src/shared/common.py` with path resolution:
- **Single-tenant**: `get_data_dir()` returns `mcc/data`
- **Multitenant**: `get_directory_for_domain(domain)` returns `mcc/domains/<domain>`

### 5. Create DBContext

Create `src/shared/db/db_context.py` for SQLModel/SQLAlchemy session management with WAL mode.
- **Single-tenant**: Static methods, single engine
- **Multitenant**: Instance-based, per-domain engines

### 6. Add Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "typer>=0.9.0",
]
```

### 7. Run Database Setup

```bash
# Create database with schema and migrations
uv run python setup_db.py create

# Or reset database
uv run python setup_db.py local
```

### 8. Update README.md

Add database section to README.md.

## Migration System

Migrations are SQL files in `src/shared/db/scripts/migrations/` directory.

### Naming Convention

```
NNN_description.sql
```

Examples:

- `001_add_can_edit_users.sql`
- `002_add_must_change_password.sql`

### Migration File Format

```sql
-- Migration: NNN_description
-- Brief description of what this migration does

ALTER TABLE table_name ADD COLUMN column_name TYPE DEFAULT value;
```

### How Migrations Work

1. Schema creation runs `create_schema.sql` first
2. `run_migrations()` checks `migrations` table for applied migrations
3. New migration files (sorted by name) are executed in order
4. Each applied migration is recorded in `migrations` table

## Database Naming Convention

**CRITICAL**: The SQLite database file MUST always be named `data.db`. Never use project-specific names like `pipeline.db` or `accounts.db`.

## File Structure

After setup:

### Single-Tenant

```
<project-root>/
├── setup_db.py                    # Database setup script
├── mcc/
│   └── data/
│       └── data.db                # SQLite database file
├── src/
│   └── shared/
│       ├── common.py              # Path utilities
│       └── db/
│           ├── __init__.py
│           ├── db_context.py      # Session manager
│           └── scripts/
│               ├── create_schema.sql
│               ├── demo_data.sql
│               └── migrations/
│                   └── *.sql
└── README.md
```

### Multitenant

```
<project-root>/
├── setup_db.py                    # Database setup script
├── mcc/
│   └── domains/
│       └── localhost/
│           └── data.db            # Per-domain SQLite database
├── src/
│   └── shared/
│       ├── common.py              # Domain path utilities
│       └── db/
│           ├── __init__.py
│           ├── db_context.py      # Session manager (per-domain)
│           └── scripts/
│               ├── create_schema.sql
│               ├── demo_data.sql
│               └── migrations/
│                   └── *.sql
└── README.md
```

## Commands

| Command           | Description                             |
| ----------------- | --------------------------------------- |
| `create`          | Create schema and run migrations        |
| `drop`            | Drop database file                      |
| `local`           | Reset database                          |
| `run --cmd <sql>` | Execute SQL command                     |

Multitenant mode adds `--domain` / `-d` flag to each command.

## Data Directory

### Single-Tenant

The data directory defaults to `mcc/data` for local development. In production, set the `DATA_DIR` environment variable.

```python
def get_data_dir() -> Path:
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir)
    return Path(__file__).parent.parent.parent.absolute() / "mcc" / "data"
```

### Multitenant

Each domain has its own data directory under `mcc/domains/<domain>`.

```python
def get_directory_for_domain(domain: str) -> Path:
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir) / domain
    return Path(__file__).parent.parent.parent.absolute() / "mcc" / "domains" / domain
```

## Templates

See `references/sqlite-setup.md` for:

- Complete setup_db.py templates (both modes)
- DBContext classes (both modes)
- Common utilities (both modes)
- Schema templates
- Migration patterns
