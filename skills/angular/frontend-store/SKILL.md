---
name: frontend-store
description: |
---

# Frontend Store Creation

Create store services using base stores for key-based signal storage.

## When to Use

- Adding state management for a new feature
- Creating stores to cache API responses
- Implementing reactive data patterns with signals
- Managing collections or single objects by key

## Prerequisites

1. Backend API must be ready
2. TypeScript DTOs generated via `uv run after_api_change.py`

## File Location

`src/ui/src/app/features/<feature>/services/<feature>-<optional-kind>-store.service.ts`

## Instructions

1. Choose appropriate store type(s) based on data needs
2. Create store service using templates from `references/store-templates.md`
3. Verify build: `nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20`

## Available Base Stores

Located at `src/ui/src/app/core/base-store/`:

| Store                      | Purpose                        | Example Use       |
| -------------------------- | ------------------------------ | ----------------- |
| `ListStore<T>`             | Collections keyed by string    | Items by parentId |
| `ObjectStore<T>`           | Single objects keyed by string | Item by id        |
| `ValueStore<T>`            | Single value (not keyed)       | Current user      |
| `ListStoreWithObject<T,O>` | List + metadata with same key  | Paginated lists   |

## Recommended Patterns

### Pattern 1: ListStore (Summary) + ObjectStore (Full) - PREFERRED

Use when list views need only summary data and detail views need full objects:

```typescript
readonly listItemsStore = new ListStore<FeatureSummaryDTO>();  // For list views
readonly itemStore = new ObjectStore<FeatureDTO>();            // For detail views
```

**When updating itemStore**: Either clear listItemsStore OR update the item in all lists where it exists.

### Pattern 2: ID List + Entity Store (Normalized)

Use when list and detail views use the same DTO:

```typescript
readonly itemEntities = new ObjectStore<FeatureDTO>();         // Full items by ID
readonly searchResults = new ListStore<{ id: string }>();      // Just IDs per search
```

List views use computed signals that join IDs to entities.

### Pattern 3: Simple ListStore

Use for simple resources loaded all at once:

```typescript
readonly itemsStore = new ListStore<FeatureDTO>();
```

## Key Rules

1. **Use base stores**: Choose appropriate store type for your data
2. **Key-based access**: Stores use string keys (e.g., parentId) to organize data
3. **Null = not loaded**: `get(key)` returns `Signal<T | null>` - null means not yet loaded
4. **Pure store**: No business logic, only state management
5. **Invalidation**: Use store's `clear()` or `remove(key)` methods directly
6. **Update propagation**: When updating ObjectStore, decide whether to clear or update related ListStores

## Reference

See `references/store-templates.md` for complete implementation examples with all three patterns.


