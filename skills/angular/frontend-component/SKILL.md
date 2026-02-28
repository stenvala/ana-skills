---
name: frontend-component
description: Create Angular standalone components as route, presentational, or shared types
---

# Frontend Component Creation

Create Angular standalone components following the controller/view pattern.

## Component Types

### 1. Route Components (Controllers)
- Handle routing, loading states, pagination, and navigation
- Inject services and manage state
- **Naming**: Prefix `route-` + descriptive name (e.g., `route-feature-list`)
- **Selector**: `route-<name>` (e.g., `route-feature-list`)
- **Class**: `Route<Name>Component` (e.g., `RouteFeatureListComponent`)
- Location: `src/ui/src/app/features/<feature>/components/route-<name>/`
- **Examples**:
  - Feature folder: `deployments/` → `route-deployments-detail`, `RouteDeploymentsDetailComponent`
  - Feature folder: `builds/` → `route-builds`, `RouteBuildsComponent`
  - Feature folder: `repositories/` → `route-repositories-detail`, `RouteRepositoriesDetailComponent`

### 2. Presentational Components (Views)
- Receive data via `input()`, emit events via `output()`
- No routing logic - purely presentational
- **Naming**: Use **exact feature folder name** as prefix (plural or singular as folder is named)
- **Selector**: `app-<feature>-<name>` (e.g., `app-deployments-header`)
- **Class**: `<Feature><Name>Component` (e.g., `DeploymentsHeaderComponent`)
- Location: `src/ui/src/app/features/<feature>/components/<name>/`
- **CRITICAL**: The `<feature>` prefix MUST match the feature folder name exactly
- **Examples**:
  - Feature folder: `deployments/` → `deployments-header`, `deployments-logs`, `DeploymentsHeaderComponent`, `DeploymentsLogsComponent`
  - Feature folder: `builds/` → `builds-list`, `builds-filter`, `BuildsListComponent`, `BuildsFilterComponent`
  - Feature folder: `repositories/` → `repositories-card`, `RepositoriesCardComponent`

### 3. Shared Components
- Reusable across the entire application
- Prefix: `shared-` (e.g., `shared-pdf-viewer`, `shared-empty-state`)
- Location: `src/ui/src/app/shared/components/<name>/`
- **IMPORTANT**: Must be registered in `src/ui/src/app/shared/shared.module.ts`
- **No SharedModule import**: Only import `[CoreModule, MaterialModule]` to avoid circular dependency

## When to Use

- **Route components**: Creating route pages (list, detail, editor views)
- **Presentational components**: Building reusable UI pieces, extracting complex view logic
- **Shared components**: Creating app-wide reusable components (loading states, empty states, viewers)

## ⚠️ CRITICAL: Component Naming Convention

**The `<feature>` prefix in component names MUST match the feature folder name exactly. This is not optional.**

### Common Mistake:
```typescript
// ❌ WRONG: Feature folder is "deployments" but using "deployment" prefix
// Feature folder: src/ui/src/app/features/deployments/
// Component name: deployment-header (INCORRECT)
// Class name: DeploymentHeaderComponent (INCORRECT)

// ✅ CORRECT: Feature folder "deployments" uses "deployments" prefix
// Feature folder: src/ui/src/app/features/deployments/
// Component name: deployments-header (CORRECT)
// Class name: DeploymentsHeaderComponent (CORRECT)
// Selector: app-deployments-header (CORRECT)
```

This applies even if the folder name is singular or plural. Always use the exact folder name.

## Prerequisites

Business logic service must exist (use `/frontend-service`).

## File Locations

### Route Components
- **Component**: `src/ui/src/app/features/<feature>/components/route-<name>/route-<name>.component.ts`
- **Template**: `src/ui/src/app/features/<feature>/components/route-<name>/route-<name>.component.html`
- **Styles**: `...component.scss` (only for exceptional cases)

### Presentational Components
- **Component**: `src/ui/src/app/features/<feature>/components/<name>/<name>.component.ts`
- **Template**: `src/ui/src/app/features/<feature>/components/<name>/<name>.component.html`
- **Styles**: `...component.scss` (only for exceptional cases)
- **Export**: Add to `src/ui/src/app/features/<feature>/components/index.ts`

### Shared Components
- **Component**: `src/ui/src/app/shared/components/shared-<name>/shared-<name>.component.ts`
- **Template**: `src/ui/src/app/shared/components/shared-<name>/shared-<name>.component.html`
- **Styles**: `...component.scss` (only for exceptional cases)
- **Register**: Add to `SHARED_COMPONENTS` array in `src/ui/src/app/shared/shared.module.ts`

## Instructions

### Route Components

1. Create TypeScript, HTML files
2. Add path constants to `paths.ts` and route configuration to `app.routes.ts`
3. Verify build

### Presentational Components

1. Create TypeScript, HTML files
2. Export from feature's `components/index.ts`
3. Import in parent route component
4. Verify build

### Shared Components

1. Create TypeScript, HTML files in `src/ui/src/app/shared/components/shared-<name>/`
2. Import component in `shared.module.ts` and add to `SHARED_COMPONENTS` array
3. Component is now available via `SharedModule` import
4. Verify build

### Verify Build

```bash
nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20
```

## Key Rules

### All Components
1. **Module imports**: Always use `[CoreModule, MaterialModule, SharedModule]` - never import Mat\* separately. Exception: Shared components (`src/ui/src/app/shared/`) only import `[CoreModule, MaterialModule]` (no SharedModule to avoid circular dependency)
2. **Standalone**: Always use `standalone: true` in the component decorator
3. **OnPush change detection**: Always use `ChangeDetectionStrategy.OnPush`
4. **Computed signals**: Use `computed()` for all reactive data
5. **No subscriptions**: Never subscribe in components
6. **Effects only for initialization**: Use `effect()` with `untracked()` only for initializing form values from loaded data
7. **Separate template**: Always put HTML in separate `.html` file
8. **Global styles**: Use classes from `src/ui/src/styles/` - minimize custom SCSS. See `/frontend-design-system` for the complete class reference

### data-test-id — MANDATORY for E2E Testing

**Every component template MUST include `data-test-id` attributes on ALL important interactive and content elements.** This is critical for reliable E2E test selectors. Missing `data-test-id` attributes block test automation.

**Elements that MUST have `data-test-id`:**
- **All buttons** (submit, cancel, delete, navigation, menu triggers, icon-only buttons)
- **All form inputs** (`<input>`, `<textarea>`, `<mat-select>`, `<mat-slide-toggle>`, `<mat-checkbox>`, etc.)
- **All form fields** (`<mat-form-field>`) — put `data-test-id` on the `mat-form-field` wrapper
- **Page headings** (`<h1>`, `<h2>`, etc.) that identify the page or section
- **Table rows** (`<tr mat-row>`) — use dynamic ID with row identifier
- **Displayed data values** (status badges, amounts, names, dates) that tests may assert on
- **Links and navigation elements** that tests may click
- **Empty states and loading indicators** to verify page state
- **Dialog containers** and dialog action buttons
- **Menu items** (`<button mat-menu-item>`)

**Naming convention:** `data-test-id="<context>-<element>-<identifier>"`
- Use kebab-case
- Include the entity/context: `data-test-id="item-delete-btn"`, `data-test-id="filter-fiscal-year-select"`
- For dynamic rows/items, include the identifier: `data-test-id="item-row-{{ item.id }}"`, `data-test-id="delete-btn-{{ item.id }}"`
- For page-level elements: `data-test-id="page-title"`, `data-test-id="create-btn"`, `data-test-id="back-btn"`

**Examples:**
```html
<!-- Page header -->
<h1 data-test-id="page-title">Items</h1>
<button matButton class="btn-action" (click)="openCreateDialog()" data-test-id="create-btn">
  <mat-icon>add</mat-icon> Add new
</button>

<!-- Form inputs -->
<mat-form-field appearance="outline" data-test-id="name-field">
  <input matInput [formField]="editForm.name" data-test-id="name-input" />
</mat-form-field>
<mat-form-field appearance="outline" data-test-id="type-field">
  <mat-select [formField]="filterForm.type" data-test-id="type-select">...</mat-select>
</mat-form-field>

<!-- Table rows and cells -->
<tr mat-row *matRowDef="let row; columns: displayedColumns" data-test-id="item-row-{{ row.id }}"></tr>
<td mat-cell *matCellDef="let row" data-test-id="item-name-{{ row.id }}">{{ row.name }}</td>
<span class="status-badge" data-test-id="item-status-{{ row.id }}">{{ row.status }}</span>

<!-- Row action buttons -->
<button mat-menu-item (click)="openEditDialog(row)" data-test-id="edit-btn-{{ row.id }}">
  <mat-icon>edit</mat-icon> <span>Edit</span>
</button>
<button mat-menu-item (click)="onDelete(row)" data-test-id="delete-btn-{{ row.id }}">
  <mat-icon>delete</mat-icon> <span>Delete</span>
</button>

<!-- Empty state and loading -->
<shared-empty-state ... data-test-id="empty-state"></shared-empty-state>
<shared-loading-bar data-test-id="loading-spinner"></shared-loading-bar>
```

**Do NOT skip this.** If a template has buttons, inputs, headers, or rendered values without `data-test-id`, it is incomplete.

### Route Components
9. **Services via inject()**: Use `private readonly service = inject(ServiceClass)`
10. **Route params via computed**: `itemId = computed(() => this.nav.routeParamMap()['id'])`
11. **Active data via nested computed**: `computed(() => { const id = this.itemId(); if (!id) return null; return this.service.item(id)(); })`
12. **Loading = null**: Derive loading state via `computed(() => this.data() === null)` — NEVER use `isLoading = signal(false)` with manual ngOnInit loading
13. **No ngOnInit data loading**: Services auto-load via `untracked()` when data signal is null — don't call `loadData()` manually
14. **Navigation**: Use `CoreNavService.goto()` with `PATHS` constants
15. **Error handling**: Use `SharedNotificationService` for user feedback
16. **Arrow functions**: Use arrow functions for `sharedLoadingButton` directive
17. **Empty states**: Use `<shared-empty-state>` component (NOT `shared-empty-content`)
18. **Loading states**: Use `<shared-loading-bar />` for data loading, or `<shared-loading-bar>` for inline spinners
19. **Dialog opening**: Always use static `DialogComponent.open(dialog, data)` method, never `dialog.open(...)`

**Paginated List Pattern** (see `RouteBuildsComponent` for reference):
- Use `signal<string>('')` for each filter, NOT form models
- Derive composite search params in one `computed()`: `search = computed(() => ({ parentId: this.selectedParentId() || undefined, ... }))`
- Data computed from search: `items = computed(() => { const s = this.search(); return this.service.items(s.parentId, s.status, s.offset)(); })`
- Total computed similarly: `total = computed(() => { const s = this.search(); return this.service.total(s.parentId, s.status)(); })`
- **Reset offset on every filter change**: `this.currentOffset.set(0)` in every filter change handler
- Import `PAGE_SIZE` from service and expose as class property for template

**Detail View Pattern** (see `RouteBuildsDetailComponent` for reference):
- Route param: `private readonly itemId = computed(() => this.nav.routeParamMap()['id'])`
- Item with null guard: `readonly item = computed(() => { const id = this.itemId(); if (!id) return null; return this.service.item(id)(); })`
- Related data separately: `readonly logContent = computed(() => { const id = this.itemId(); if (!id) return null; return this.service.logContent(id)(); })`
- Derived state: `readonly hasArtifacts = computed(() => { const item = this.item(); return item !== null && item.status === 'succeeded'; })`

**CRITICAL — Loading State Pattern:**
```typescript
// ❌ WRONG PATTERN — Never do this:
export class MyComponent implements OnInit {
  isLoading = signal(false);
  data = signal<Data[] | null>(null);

  async ngOnInit() {
    this.isLoading.set(true);
    const result = await this.service.loadData();
    this.data.set(result);
    this.isLoading.set(false);
  }
}

// ✅ CORRECT PATTERN — Always do this:
export class MyComponent {
  // Data from service (auto-loads via untracked when null)
  readonly items = computed(() => {
    const s = this.search();
    return this.service.items(s.parentId, s.status, s.offset)();
  });

  // Loading derived from data being null
  readonly isLoading = computed(() => this.items() === null);
}
```

**Side Note — Polling**: Some features need real-time updates (e.g., builds). This requires `OnInit`/`OnDestroy` with `setInterval`/`clearInterval`. See `route-component-template.md` for the polling lifecycle pattern. This is NOT standard for all components.

### Presentational Components
18. **Inputs**: Use `input<Type>()` function, not `@Input()` decorator
19. **Outputs**: Use `output<Type>()` function, not `@Output()` decorator
20. **Computed from inputs**: Derive state with `computed(() => this.myInput())`
21. **TrackBy**: Provide trackBy functions for `@for` loops
22. **Helper methods**: Add formatting/logic helpers for template
23. **Content projection**: Use `@ContentChild` for optional template slots

### Shared Components
24. **No SharedModule import**: Only use `imports: [CoreModule, MaterialModule]` - never import SharedModule (circular dependency)
25. **Register in SharedModule**: Add to `SHARED_COMPONENTS` array in `shared.module.ts`
26. **Prefix naming**: Always use `shared-` prefix (e.g., `shared-pdf-viewer`, `SharedPdfViewerComponent`)
27. **Same patterns as presentational**: Use `input()`, `output()`, `computed()`, OnPush change detection

## Design System

For all layout decisions, page structure, CSS class references, button types, card patterns, info-grid usage, table design, status badges, and responsive design, use the `/frontend-design-system` skill. That skill contains the complete design system documentation.

This skill focuses on component architecture, naming conventions, and TypeScript patterns only.

## Templates

The `references/` folder contains complete, self-contained implementation templates. Use these as copy-paste starting points — they ARE the reference implementations.

| Template | What It Contains | Use When |
|----------|-----------------|----------|
| `route-component-template.md` | Paginated list pattern, detail view pattern, polling lifecycle | Creating route components |
| `presentational-component-template.md` | Input/output pattern, computed from inputs, content projection | Creating feature presentational components |
| `shared-component-template.md` | SharedModule registration, no-SharedModule-import rule | Creating shared components |
| `view-template.md` | Loading/data/empty-state HTML patterns | Building any component template |
| `routing-template.md` | Path constants, route config, navigation usage | Adding routes for new components |

**How to use**: Pick the template matching your component type, copy the TypeScript and HTML patterns, and replace `Feature`/`Item` placeholders with your actual names.
