---
name: database-setup-sqlite
description: |
  Set up an SQLite database for the project with setup_db.py script, schema creation, and migrations.
  Use when: Creating a new SQLite database for local development or simple applications.
---

# Setup SQLite Database

Create an SQLite database with setup script, schema initialization, and migration support.

## When to Use

- Setting up a new SQLite database for local development
- Need file-based database with multi-domain support
- Projects requiring migration support
- Simple applications without PostgreSQL dependency

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

Create the setup script from `references/sqlite-setup.md` template in the project root.

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

Create `src/shared/common.py` for domain path resolution.

### 5. Create DBContext

Create `src/shared/db/db_context.py` for SQLModel/SQLAlchemy session management.

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

# Or reset with demo data
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

## File Structure

After setup:

```
<project-root>/
├── setup_db.py                    # Database setup script
├── mcc/
│   └── domains/
│       └── localhost/
│           └── data.db            # SQLite database file
├── src/
│   └── shared/
│       ├── common.py              # Domain utilities
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

## Commands

| Command           | Description                             |
| ----------------- | --------------------------------------- |
| `create`          | Create schema and run migrations        |
| `drop`            | Drop database file                      |
| `demo_data`       | Add demo data                           |
| `local`           | Reset localhost database with demo data |
| `run --cmd <sql>` | Execute SQL command                     |

## Domain-Based Multitenancy

SQLite databases are stored per domain in `mcc/domains/<domain>/data.db`.

- `localhost` - Local development
- `example.com` - Production domain

Use `--domain` flag or `DBContext("domain")` to switch domains.

## Templates

See `references/sqlite-setup.md` for:

- Complete setup_db.py template
- DBContext class
- Common utilities
- Schema templates
- Migration patterns
