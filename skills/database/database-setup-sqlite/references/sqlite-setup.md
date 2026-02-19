# SQLite Database Setup

SQLite is a file-based database ideal for local development and simple applications.

## Database Location

SQLite databases are stored at: `mcc/domains/<domain>/data.db`

Default domain is `localhost` for local development.

## setup_db.py Template

```python
#!/usr/bin/env python3
"""Database setup script using SQLite."""

import sqlite3
from pathlib import Path

import typer

app = typer.Typer(help="Setup SQLite database")

DEFAULT_DOMAIN = "localhost"


def get_db_path(domain: str = DEFAULT_DOMAIN) -> Path:
    """Get database path for a domain. Default is localhost for local development."""
    db_dir = Path(__file__).parent / "mcc" / "domains" / domain
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "data.db"


def get_scripts_path() -> Path:
    """Get path to SQL scripts."""
    return Path(__file__).parent / "src" / "shared" / "db" / "scripts"


def get_migrations_path() -> Path:
    """Get path to migration scripts."""
    return get_scripts_path() / "migrations"


def execute_sql_file(conn: sqlite3.Connection, file_path: Path, description: str) -> bool:
    """Execute SQL file."""
    if not file_path.exists():
        print(f"WARNING: {description} file not found at: {file_path}")
        return False

    with open(file_path, "r") as f:
        sql_content = f.read()

    cursor = conn.cursor()
    cursor.executescript(sql_content)
    conn.commit()
    print(f"PASS: {description} executed successfully.")
    return True


def run_migrations(conn: sqlite3.Connection) -> None:
    """Run pending migrations."""
    migrations_path = get_migrations_path()
    if not migrations_path.exists():
        print("WARNING: Migrations directory not found.")
        return

    cursor = conn.cursor()

    # Get list of already applied migrations
    cursor.execute("SELECT name FROM migrations")
    applied = {row[0] for row in cursor.fetchall()}

    # Get all migration files sorted by name
    migration_files = sorted(migrations_path.glob("*.sql"))

    for migration_file in migration_files:
        migration_name = migration_file.stem
        if migration_name in applied:
            print(f"SKIP: Migration {migration_name} already applied.")
            continue

        print(f"APPLY: Running migration {migration_name}...")
        with open(migration_file, "r") as f:
            sql_content = f.read()

        try:
            cursor.executescript(sql_content)
            cursor.execute(
                "INSERT INTO migrations (name) VALUES (?)", (migration_name,)
            )
            conn.commit()
            print(f"PASS: Migration {migration_name} applied successfully.")
        except sqlite3.Error as e:
            print(f"ERROR: Migration {migration_name} failed: {e}")
            raise


def _create_schema(domain: str = DEFAULT_DOMAIN) -> None:
    """Create database schema and run migrations."""
    db_path = get_db_path(domain)
    print(f"Creating schema in: {db_path}")

    conn = sqlite3.connect(str(db_path))
    try:
        scripts_path = get_scripts_path()
        execute_sql_file(conn, scripts_path / "create_schema.sql", "Schema creation")
        print(f"PASS: Schema created: {db_path}")
        run_migrations(conn)
    except sqlite3.Error as e:
        print(f"ERROR: Error creating schema: {e}")
    finally:
        conn.close()


def _drop_db(domain: str = DEFAULT_DOMAIN) -> None:
    """Drop database by deleting the file."""
    db_path = get_db_path(domain)
    print(f"Dropping database: {db_path}")

    if db_path.exists():
        db_path.unlink()
        print(f"PASS: Database dropped: {db_path}")
    else:
        print(f"WARNING: Database not found: {db_path}")


def _add_demo_data(domain: str = DEFAULT_DOMAIN) -> None:
    """Add demo data to database."""
    db_path = get_db_path(domain)
    print(f"Adding demo data to: {db_path}")

    if not db_path.exists():
        print("ERROR: Database does not exist. Create schema first.")
        return

    conn = sqlite3.connect(str(db_path))
    try:
        scripts_path = get_scripts_path()
        demo_data_file = scripts_path / "demo_data.sql"
        if demo_data_file.exists():
            execute_sql_file(conn, demo_data_file, "Demo data")
            print("PASS: Demo data added successfully.")
        else:
            print("WARNING: No demo data file found.")
    except sqlite3.Error as e:
        print(f"ERROR: Error adding demo data: {e}")
    finally:
        conn.close()


@app.command()
def create(
    domain: str = typer.Option(DEFAULT_DOMAIN, "--domain", "-d", help="Domain name"),
) -> None:
    """Create database schema."""
    _create_schema(domain)


@app.command()
def drop(
    domain: str = typer.Option(DEFAULT_DOMAIN, "--domain", "-d", help="Domain name"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation"),
) -> None:
    """Drop database."""
    if not confirm:
        db_path = get_db_path(domain)
        typer.confirm(f"Drop database '{db_path}'? This cannot be undone!", abort=True)
    _drop_db(domain)


@app.command()
def demo_data(
    domain: str = typer.Option(DEFAULT_DOMAIN, "--domain", "-d", help="Domain name"),
) -> None:
    """Add demo data to database."""
    _add_demo_data(domain)


@app.command()
def local() -> None:
    """Reset and initialize localhost database with demo data."""
    print("Resetting and initializing localhost database...")
    _drop_db(DEFAULT_DOMAIN)
    _create_schema(DEFAULT_DOMAIN)
    _add_demo_data(DEFAULT_DOMAIN)
    print("PASS: Localhost database ready!")


@app.command()
def run(
    domain: str = typer.Option(DEFAULT_DOMAIN, "--domain", "-d", help="Domain name"),
    cmd: str = typer.Option(..., "--cmd", help="SQL command to execute"),
) -> None:
    """Execute arbitrary SQL command against database."""
    db_path = get_db_path(domain)
    print(f"Executing SQL on: {db_path}")
    print(f"Command: {cmd}\n")

    if not db_path.exists():
        print("ERROR: Database does not exist.")
        raise typer.Exit(1)

    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        cursor.execute(cmd)

        if cursor.description:
            rows = cursor.fetchall()
            if rows:
                col_names = [desc[0] for desc in cursor.description]
                print(" | ".join(col_names))
                print("-" * (len(" | ".join(col_names))))
                for row in rows:
                    print(" | ".join(str(val) for val in row))
                print(f"\nPASS: Returned {len(rows)} row(s)")
            else:
                print("PASS: Query executed (0 rows)")
        else:
            conn.commit()
            print("PASS: Command executed")

    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        raise typer.Exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    app()
```

## Schema Template

Create `src/shared/db/scripts/create_schema.sql`:

```sql
-- Migrations tracking table (required for migration support)
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example tables below (customize for your project)

-- Users/Admins table
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_admins_email ON admins(email);

-- Sessions table for authentication
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL UNIQUE,
    admin_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_admin_id ON sessions(admin_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
```

## Migration Examples

### Migration: `001_add_can_edit_users.sql`

```sql
-- Migration: 001_add_can_edit_users
-- Add can_edit_users column to admins table for user management permissions

ALTER TABLE admins ADD COLUMN can_edit_users INTEGER NOT NULL DEFAULT 0;
```

### Migration: `002_add_must_change_password.sql`

```sql
-- Migration: 002_add_must_change_password
-- Add must_change_password column to admins table

ALTER TABLE admins ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0;
```

## DBContext Class

Create `src/shared/db/db_context.py` for database session management:

```python
"""
Database context manager for handling SQLite database connections and sessions.

Provides centralized database session management with domain-based multitenancy.
Each domain has its own SQLite database file.
"""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from shared.common import get_directory_for_domain


class DBContext:
    """Database context manager for session handling and multitenancy."""

    _engines: dict[str, Engine] = {}

    def __init__(self, domain: str = "localhost") -> None:
        self.domain = domain

    def _get_db_path(self) -> Path:
        """Get database path for current domain."""
        db_dir = get_directory_for_domain(self.domain)
        return db_dir / "data.db"

    def _get_engine(self) -> Engine:
        """Get or create database engine for current domain."""
        if self.domain not in DBContext._engines:
            db_path = self._get_db_path()
            database_url = f"sqlite:///{db_path}"
            DBContext._engines[self.domain] = create_engine(
                database_url,
                echo=False,
                connect_args={"check_same_thread": False},
            )

        return DBContext._engines[self.domain]

    def dispose_engines(self) -> None:
        """Dispose all cached engines to free database connections."""
        for engine in DBContext._engines.values():
            engine.dispose()
        DBContext._engines.clear()

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic transaction management.

        Provides:
        - Automatic session creation
        - Automatic transaction commit on success
        - Automatic transaction rollback on exception
        - Automatic session cleanup

        Usage:
            with DBContext().get_db_session() as session:
                # Use session for database operations

            # Or with specific domain:
            with DBContext("example.com").get_db_session() as session:
                # Use domain-specific database
        """
        engine = self._get_engine()

        with Session(engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
```

## Common Utilities

Create `src/shared/common.py` for shared utilities:

```python
"""Common utilities shared across modules."""

import os
from pathlib import Path


def get_directory_for_domain(domain: str) -> Path:
    """Get the directory path for a domain's data."""
    if os.environ.get("ENV_TYPE") == "PROD":
        return Path("/path/to/prod/domains") / domain
    return Path(__file__).parent.parent.parent.absolute() / "mcc" / "domains" / domain
```

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "sqlmodel>=0.0.22",
    "typer>=0.9.0",
]
```

## README.md Section

Add to project README.md:

```markdown
## Database

This project uses **SQLite** for data storage. Database files are stored in `mcc/domains/<domain>/data.db`.

### Setup

```bash
# Create database schema
uv run python setup_db.py create

# Reset and initialize with demo data
uv run python setup_db.py local

# Drop database
uv run python setup_db.py drop --confirm

# Execute SQL command
uv run python setup_db.py run --cmd "SELECT * FROM admins"
```

### Migrations

Migrations are stored in `src/shared/db/scripts/migrations/` and run automatically during schema creation.

To add a new migration:
1. Create `src/shared/db/scripts/migrations/NNN_description.sql`
2. Run `uv run python setup_db.py create` to apply
```

## SQLite Type Mappings

| Python Type | SQLite Type | Notes |
|-------------|-------------|-------|
| `int` | `INTEGER` | |
| `str` | `TEXT` | |
| `float` | `REAL` | |
| `bool` | `INTEGER` | 0=False, 1=True |
| `datetime` | `TIMESTAMP` | Stored as TEXT |
| `bytes` | `BLOB` | |

## Index Best Practices

```sql
-- Single column index for lookups
CREATE INDEX IF NOT EXISTS idx_table_column ON table(column);

-- Composite index for multi-column queries
CREATE INDEX IF NOT EXISTS idx_table_col1_col2 ON table(col1, col2);

-- Partial index for filtered queries
CREATE INDEX IF NOT EXISTS idx_table_active ON table(column) WHERE is_active = 1;
```

## Foreign Key Patterns

```sql
-- Cascade delete (remove child when parent deleted)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE CASCADE

-- Set null (keep child, set FK to null)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE SET NULL

-- Restrict (prevent parent deletion if children exist)
FOREIGN KEY (parent_id) REFERENCES parents(id) ON DELETE RESTRICT
```
