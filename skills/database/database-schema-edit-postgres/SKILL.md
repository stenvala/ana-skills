---
name: database-schema-edit-postgres
description: |
  Create or modify PostgreSQL database schema from data model design.
  Use when: Implementing PostgreSQL database tables after design approval, adding columns to existing tables,
  creating indexes, or adding foreign key constraints. For SQLite projects, use database-schema-edit-sqlite instead.
---

# Database Schema Edit (PostgreSQL)

Edit PostgreSQL schema to implement data model designs.

## Prerequisites

Database design must exist in `docs/datamodels/<domain>.md` (use `/database-design` first).

## File Location

Schema file: `src/shared/db/scripts/create_schema.sql`

## Instructions

### 1. Locate Schema Section

Tables are grouped by domain in the schema file. Find the appropriate section or create a new one.

### 2. Handle Both Scenarios

When editing schema, consider:
- **New databases**: Table will be created fresh
- **Existing databases**: Need migration support

### 3. Create Table Definition

Add table with proper constraints, foreign keys, and indexes.

### 4. Add Migration Support

In the `SCHEMA MODIFICATION SUPPORT` section, add `ALTER TABLE` statements for existing databases.

### 5. Verify Schema

```bash
uv run python setup_db.py drop --confirm main
uv run python setup_db.py create main
uv run python setup_db.py demo_data main
```

## Key Rules

1. **Primary keys**: Always `VARCHAR(255) PRIMARY KEY DEFAULT gen_random_uuid()::text`
2. **Foreign keys**: Add `ON DELETE CASCADE` or `ON DELETE SET NULL` as appropriate
3. **Timestamps**: Use `TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP`
4. **Enums**: Use CHECK constraints: `CHECK (status IN ('ACTIVE', 'INACTIVE', 'DELETED'))`
5. **Indexes**: Create for all foreign keys and frequently queried fields
6. **JSONB**: Use `JSONB` type for JSON data with indexing support

## Templates

See `references/schema-examples.md` for examples of:
- Creating new tables
- Adding columns to existing tables
- Creating indexes
- Adding migration support
