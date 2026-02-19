---
name: frontend-component
description: |
---

# Frontend Component Creation

Create Angular standalone components following the controller/view pattern.

## Component Types

### 1. Route Components (Controllers)
- Handle routing, loading states, pagination, and navigation
- Inject services and manage state
- Prefix: `route-` (e.g., `route-feature-list`)
- Location: `src/ui/src/app/features/<feature>/components/route-<name>/`

### 2. Presentational Components (Views)
- Receive data via `input()`, emit events via `output()`
- No routing logic - purely presentational
- Prefix: `<feature>-` or descriptive name (e.g., `event-list-viewer`)
- Location: `src/ui/src/app/features/<feature>/components/<name>/`

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
2. **Standalone is default**: Don't specify `standalone: true`
3. **OnPush change detection**: Always use `ChangeDetectionStrategy.OnPush`
4. **Computed signals**: Use `computed()` for all reactive data
5. **No subscriptions**: Never subscribe in components
6. **Effects only for initialization**: Use `effect()` with `untracked()` only for initializing form values from loaded data
7. **Separate template**: Always put HTML in separate `.html` file
8. **Global styles**: Use classes from `src/ui/src/styles/` - minimize custom SCSS

### Route Components
9. **Services via inject()**: Use `private service = inject(ServiceClass)`
10. **Route params via computed**: `formId = computed(() => this.nav.routeParamMap()['paramName'])`
11. **Active data via nested computed**: `computed(() => { const id = this.formId(); if (!id) return null; return this.service.getData(id)(); })`
12. **Loading = null**: Derive loading state via `computed(() => this.data() === null)` - NEVER use `isLoading = signal(false)` with manual ngOnInit loading
13. **No ngOnInit data loading**: Services auto-load via `untracked()` when data signal is null - don't call `loadData()` manually
14. **Navigation**: Use `CoreNavService.goto()` with `PATHS` constants
15. **Error handling**: Use `MatSnackBar` for error messages
16. **Arrow functions**: Use arrow functions for `sharedLoadingButton` directive
17. **Empty states**: Use `<shared-empty-state>` component (NOT `shared-empty-content`)
18. **Loading states**: Use `<shared-loading-bar />` for data loading, or `<shared-loading-spinner>` for inline spinners
19. **Dialog opening**: Always use static `DialogComponent.open(dialog, data)` method, never `dialog.open(...)`

**CRITICAL - Loading State Pattern:**
```typescript
// ❌ WRONG PATTERN - Never do this:
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

// ✅ CORRECT PATTERN - Always do this:
export class MyComponent {
  // Route param as computed
  itemId = computed(() => this.nav.routeParamMap()['itemId']);

  // Data from service (auto-loads via untracked when null)
  data = computed(() => {
    const id = this.itemId();
    if (!id) return null;
    return this.service.getById(id)();
  });

  // Loading derived from data being null
  isLoading = computed(() => this.data() === null);
}
```

The service's `getById()` or `getAll()` methods handle auto-loading:
```typescript
// In service
getById(id: string): Signal<Data | null> {
  const signal = this.state.getItem(id);
  if (signal() === null) {
    untracked(() => this.loadById(id));
  }
  return signal;
}
```

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

## Global Style Classes

Global styles are in `src/ui/src/styles/`. Always prefer these over custom SCSS.

### Layout (`_layout.scss`)
- `page-centered` - Full page centered container (login, register)
- `page-with-toolbar` - Full page with toolbar layout
- `content-wrapper` - Content area with max-width
- `flex`, `flex-col`, `flex-1`, `items-center`, `justify-center`, `justify-between` - Flexbox utilities
- `gap-xs`, `gap-sm`, `gap-md`, `gap-lg` - Gap spacing
- `spacer` - Flex spacer
- `mb-sm`, `mb-md`, `mb-lg`, `mb-xl` - Margin bottom
- `full-width` - 100% width

### Pages (`_pages.scss`)
- `page-container`, `page-container--narrow`, `page-container--wide`, `page-container--fullscreen` - Page wrappers
- `page-header`, `page-header__actions`, `page-header__info` - Page headers
- `panel-footer`, `panel-footer__header`, `panel-footer__content` - Footer panels
- `panel-with-sidebar`, `panel-with-sidebar__sidebar`, `panel-with-sidebar__main` - Sidebar layouts
- `info-grid`, `info-grid--compact`, `info-item`, `info-label`, `info-value` - Detail views
- `edit-form`, `edit-form--grid`, `edit-form__actions` - Form layouts
- `filter-form`, `filter-card` - Filter sections
- `loading-state` - Centered loading
- `content-grid`, `content-grid--reverse` - Two-column layouts

### Cards (`_cards.scss`)
- `form-card`, `form-card--md`, `form-card--lg` - Form cards
- `feature-card` - Dashboard cards with hover
- `card-icon` - Card avatar icons
- `cards-grid` - Responsive card grid
- `card-compact` - Dense card variant

### Button Types (matButton directive)

**IMPORTANT**: All buttons must use the `matButton` directive with a type. Never use plain `<button>`.

| Type | Use Case | Example |
|------|----------|---------|
| `matButton="filled"` | **Primary actions**: Submit, Save, Create, main CTA | Dialog submit, Page header "Lisää uusi" |
| `matButton="outlined"` | **Secondary actions**: Cancel, Back, alternative actions | Dialog cancel, Cancel editing |
| `matButton="tonal"` | **Subtle actions in dense UIs**: Quick action buttons, chips | Template quick-apply buttons, current state indicator |
| `matButton="elevated"` | **Floating/promoted actions**: Add in collapsed sections | "Lisää" button when section is collapsed |
| `matButton` (no value) + `class="only-icon"` | **Icon-only buttons**: Menu triggers, back buttons | `<button matButton class="only-icon">` |

**Guidelines:**
- Dialog actions: `outlined` for Cancel, `filled` for Submit/Save
- Page header actions: `filled` for primary action (Create/Add)
- Table row actions: Use icon-only buttons with menu trigger
- Inline forms: `outlined` for Cancel, `filled` for Save
- Quick-action toolbars: `tonal` for multiple related actions

**Icon requirement**: All buttons MUST have an icon (either icon-only or icon + text).

```html
<!-- Primary action -->
<button matButton="filled" (click)="onSubmit()">
  <mat-icon>save</mat-icon>
  Tallenna
</button>

<!-- Secondary action -->
<button matButton="outlined" (click)="onCancel()">
  <mat-icon>close</mat-icon>
  Peruuta
</button>

<!-- Icon-only button -->
<button matButton class="only-icon" [matMenuTriggerFor]="menu">
  <mat-icon>more_vert</mat-icon>
</button>

<!-- Tonal quick-action -->
<button matButton="tonal" (click)="applyTemplate(template)">
  {{ template.name }}
</button>
```

### Button CSS Classes (`_buttons.scss`)
- `btn-submit` - Submit button style
- `.spinning` (mat-icon) - Spinning animation
- `.loading` (button) - Loading state
- `.confirming` (button) - Confirm state (red)
- `only-icon` - For icon-only buttons (removes text padding)

### Components (`_components.scss`)
- `data-table`, `clickable-row`, `actions-cell` - Table styles
- `badge`, `badge--income`, `badge--expense`, `badge--warning`, `badge--pill` - Badges
- `status-badge`, `status-badge--open`, `status-badge--closed` - Status badges
- `amount--income`, `amount--expense` - Amount formatting
- `dialog-card`, `dialog-card--narrow`, `dialog-card--wide` - Dialog sizes
- `drop-zone`, `drop-zone--active` - File upload
- `result-box`, `result-box--success`, `result-box--error`, `result-box--warning` - Messages
- `delete-action` - Red delete button

### Forms (`_forms.scss`)
- `form` - Form container
- `dialog-subtitle` - Dialog subtitle text

### Sections (`_sections.scss`)
- `welcome-section` - Welcome header
- `panel` - Panel container

## Templates

See `references/` folder for:

- `route-component-template.md` - Route component pattern with pagination
- `presentational-component-template.md` - Feature presentational component pattern
- `shared-component-template.md` - Shared component pattern (no SharedModule import)
- `view-template.md` - HTML template patterns
- `routing-template.md` - Route configuration

