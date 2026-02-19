---
name: database-repository
description: |
  Create repository layer for database CRUD operations.
  Use when: Adding database access layer after models are created, implementing query methods,
  or creating data access patterns for services.
---

# Database Repository Creation

Create repository classes that handle database operations using the repository pattern.

## When to Use

- Creating data access layer after SQLModel classes exist
- Adding new query methods to existing repositories
- Implementing complex database queries
- Separating database operations from business logic

## Prerequisites

1. Database design exists in `docs/datamodels/<domain>.md`
2. Schema exists in `src/shared/db/scripts/create_schema.sql`
3. SQLModel class exists in `src/shared/db/models/<domain>_models/<table_name>.py`

## File Location

Create repository at: `src/shared/db/repositories/<domain>_repository/<table_name>_repository.py`

## Instructions

### 1. Create Repository Class

Implement the repository with session injection and standard CRUD methods.

### 2. Add Domain-Specific Queries

Add methods for common query patterns needed by services.

### 3. Verify Import

```bash
uv run python -c "from shared.db.repositories.<domain>_repository.<table_name>_repository import <TableName>Repository; print('OK')"
```

## Key Rules

1. **Session injection**: Accept `Session` in `__init__`, never create sessions
2. **No commits**: Use `session.flush()` not `session.commit()` - transaction managed by service layer
3. **Refresh after write**: Always call `session.refresh(entity)` after `add()` + `flush()`
4. **Return types**: Use `Optional[T]` for single results, `List[T]` for multiple
5. **Query patterns**:
   - Simple ID lookup: `session.get(Model, id)`
   - Complex queries: `select(Model).where(...)` with `session.exec(...)`
6. **List conversion**: Always wrap `session.exec(...).all()` in `list()` for proper typing

## Templates

See `references/` folder for:
- `repository-template.md` - Basic repository structure
- `query-patterns.md` - Common query patterns
