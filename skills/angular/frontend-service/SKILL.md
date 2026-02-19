---
name: frontend-service
description: Create Angular services that orchestrate API calls and state management
---

# Frontend Service Creation

Create business logic services that orchestrate API calls and state management.

## When to Use

- Creating service layer for a new feature
- Implementing CRUD operations with state updates
- Coordinating API service and state store

## Prerequisites

1. State service must exist (use `/frontend-state`)
2. API service auto-generated from backend

## File Location

Create service at: `src/ui/src/app/features/<feature>/services/<feature>.service.ts`

## Instructions

### 1. Create Service Class

Inject API service, state service, and notification service.

### 2. Implement Data Access Methods

Add `getItems()` and `getItem()` with signal returns and lazy loading.

### 3. Implement CRUD Methods

Add `create()`, `update()`, `delete()` with proper store updates.

### 4. Verify Build

```bash
nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20
```

## Key Rules

1. **Orchestration**: Coordinates API service and state service
2. **Signal from store**: Return signal from state store
3. **Untracked loading**: Use `untracked()` to trigger load if signal is null
4. **Load returns data**: Load methods return the data, not void
5. **Error handling**: Use notification service for user feedback
6. **Store updates**: On create/update, add/update items in store using `setItem()`
7. **Store removals**: On delete, use `removeItem()` to remove specific item

## Templates

See `references/service-template.md` for the complete reference implementation.


