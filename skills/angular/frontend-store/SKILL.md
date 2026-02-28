---
name: frontend-store
description: Create Angular store services using base stores for signal-based state
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

`src/ui/src/app/features/<feature>/services/<feature>-<optional-kind>.store.ts`

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

### Pattern 1: Paginated List + Detail Store — PREFERRED for paginated data

Use when the API returns paginated results with total counts and you have separate list/detail views.

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStore<FeatureDTO>();         // Lists by composite key (e.g., "repoId:status:offset")
  readonly totalStore = new ObjectStore<number>();            // Totals by key WITHOUT offset (e.g., "repoId:status")
  readonly itemStore = new ObjectStore<FeatureDetailDTO>();   // Full items by ID
}
```

The **service** defines helper functions for composite cache keys — not the store.

### Pattern 2: Non-Paginated List + Detail Store

Use when all items are loaded at once (no server-side pagination, small collections). Uses `ALL_KEY = 'all'` in the service.

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStore<FeatureDTO>();          // All items under 'all' key
  readonly itemStore = new ObjectStore<FeatureDTO>();          // Individual items by ID
}
```

### Pattern 3: Simple ListStore

For simple resources loaded all at once with no separate detail view:

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStore<FeatureDTO>();
}
```

### When to add more stores

Add additional `ObjectStore` instances for related data loaded separately:

```typescript
@Injectable({ providedIn: 'root' })
export class FeatureStoreService {
  readonly itemsStore = new ListStore<FeatureDTO>();
  readonly totalStore = new ObjectStore<number>();
  readonly itemStore = new ObjectStore<FeatureDetailDTO>();
  readonly logContentStore = new ObjectStore<string>();    // Logs loaded separately
}
```

## Key Rules

1. **Pure data container**: NO wrapper methods. Services access store instances directly
2. **Use base stores**: Choose appropriate store type for your data
3. **Key-based access**: Stores use string keys (e.g., parentId, composite keys) to organize data
4. **Null = not loaded**: `get(key)` returns `Signal<T | null>` — null means not yet loaded
5. **Invalidation**: Use store's `clear()` or `remove(key)` methods directly from the service
6. **Multiple stores**: A single store service can (and should) hold multiple store instances for different data types
7. **Composite keys**: For paginated/filtered data, the service builds composite string keys — the store doesn't know about the key structure

## Reference

See `references/store-templates.md` for complete implementation examples with all patterns and the full Store API reference.
