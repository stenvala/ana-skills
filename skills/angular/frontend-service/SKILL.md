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

1. Store must exist (use `/frontend-store`)
2. API service auto-generated from backend

## File Location

Create service at: `src/ui/src/app/features/<feature>/services/<feature>.service.ts`

## Instructions

Choose the pattern that matches your feature's data needs, then follow the corresponding template in `references/service-template.md`.

### Pattern 1: Paginated List + Detail (Template 1)

Use when the API returns paginated results with total counts. See `references/service-template.md` → Template 1.

Key elements:
- **Cache key functions** at module level (items key includes offset, total key does NOT)
- **`PAGE_SIZE`** constant exported for components
- **Signal accessors** with lazy loading (`items()`, `item()`, `total()`)
- **`search()`** stores both items AND total from paginated responses
- **Action methods** that return API response without updating list stores

### Pattern 2: Non-Paginated List + Detail (Template 2)

Use when the API returns all items at once (no pagination, small collections). See `references/service-template.md` → Template 2.

Key elements:
- **`ALL_KEY`** constant for the single list cache key
- **Signal accessors** with lazy loading (`getAll()`, `getById()`)
- **`loadAll()`** with `refresh` parameter and `isInitialized` check
- **CRUD methods** that call `loadAll()` after mutation to reload from server

### Common Patterns (Both Templates)

#### Signal Accessor Pattern

```typescript
getAll(): Signal<FeatureDTO[] | null> {
  const signal = this.store.itemsStore.get(key);
  if (signal() === null) {
    untracked(() => {
      this.loadAll();
    });
  }
  return signal;
}
```

#### Load Method Pattern

```typescript
async loadAll(refresh: boolean = true): Promise<FeatureDTO[]> {
  if (!refresh && this.store.itemsStore.isInitialized(key)) {
    return this.store.itemsStore.get(key)()!;
  }
  const response = await firstValueFrom(this.api.listItems());
  this.store.itemsStore.set(key, response.items);
  return response.items;
}
```

#### CRUD After Mutation (Non-Paginated)

```typescript
async create(dto: CreateDTO): Promise<FeatureDTO> {
  const result = await firstValueFrom(this.api.createItem(dto));
  this.store.itemStore.set(result.id, result);
  await this.loadAll();
  return result;
}
```

### Verify Build

```bash
nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20
```

## Key Rules

1. **Orchestration**: Coordinates API service and store — no direct API calls from components
2. **Signal accessors from store**: Return `this.store.someStore.get(key)` — the store's signal
3. **Untracked loading**: Use `untracked(() => { this.load(...); })` to trigger load if signal is null
4. **Load returns data**: Load methods return the data (Promise), not void
5. **Cache key functions**: Define at module level, not as class methods
6. **Total separate from items**: (Paginated only) Total key must NOT include offset
7. **CRUD reloads list**: After create/update/delete, call `loadAll()` to reload from server (non-paginated) or clear caches (paginated)
8. **Store updates on detail**: On create/update, also set the individual item in `itemStore`
9. **refresh parameter**: Defaults to `true`. Signal accessors don't pass it (use default). Components can call load methods with `refresh=true` for explicit refresh
10. **No notification in accessors**: Signal accessor methods don't show notifications — only action/CRUD methods may

## Side Note: Polling for Changes

Some features need real-time updates (e.g., builds that change status). This is a **special pattern**, not standard for all features. See `references/service-template.md` → Side Note: Polling for Changes.

## Side Note: Loading Related Data

For items with separately-loaded data (e.g., logs, metrics), add additional signal accessors and load methods following the same pattern. See `references/service-template.md` → Side Note: Loading Related Data.

## Templates

See `references/service-template.md` for complete templates for both patterns.
