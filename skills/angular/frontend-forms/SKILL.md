---
name: frontend-forms
description: Create Angular 21 signal-based form components with validation
---

# Frontend Forms Creation

Create Angular 21 signal-based form components using the modern `@angular/forms/signals` API.

## When to Use

- Creating form dialogs (create/edit operations)
- Building forms in route components (filters, search, inline edit)
- Any component that needs form validation and field binding
- Replacing existing ReactiveFormsModule forms

## Prerequisites

1. Angular 21.x installed
2. Feature module/structure exists
3. Required services available for business logic

## File Locations

### Form Dialogs
`src/ui/src/app/features/<feature>/components/<feature>-dialog-<name>/<feature>-dialog-<name>.component.ts`

### Route Component Forms
`src/ui/src/app/features/<feature>/components/route-<feature>-<name>/route-<feature>-<name>.component.ts`

## Key Concepts

### Signal-Based Forms vs ReactiveFormsModule

| Reactive Forms (Old) | Signal Forms (New) |
|---------------------|-------------------|
| `FormBuilder`, `FormGroup`, `FormControl` | `signal<T>()`, `form()` |
| `formControlName`, `formGroup` directives | `[formField]` directive |
| `Validators.required`, `Validators.email` | `required()`, `email()` from `@angular/forms/signals` |
| `form.value`, `form.valid` (properties) | `form().value()`, `form().valid()` (signals) |
| `valueChanges.subscribe()` | `computed()` on field signals |

### Core Imports

```typescript
// Angular core
import { Component, signal, computed, ChangeDetectionStrategy, inject } from '@angular/core';

// Signal forms
import { form, FormField, required, email, minLength, maxLength, pattern, min, max } from '@angular/forms/signals';

// Dialog types (for DI - NOT module imports)
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

// App modules (always use these - never import Mat* modules individually)
import { CoreModule } from '@core/core.module';
import { MaterialModule } from '@shared/material';
import { SharedModule } from '@shared/shared.module';
```

## Instructions

### 1. Define Form Model Interface

```typescript
interface MyFormModel {
  name: string;
  email: string;
  categoryId: string | null;
}
```

### 2. Create Form Model Signal

```typescript
private readonly formModel = signal<MyFormModel>({
  name: '',
  email: '',
  categoryId: null,
});
```

### 3. Create Field Tree with Validation

```typescript
protected readonly myForm = form(this.formModel, (f) => {
  required(f.name, { message: 'Name is required' });
  maxLength(f.name, 100, { message: 'Name must be at most 100 characters' });
  required(f.email, { message: 'Email is required' });
  email(f.email, { message: 'Invalid email address' });
});
```

### 4. Bind Fields in Template

```html
<mat-form-field appearance="outline" class="full-width">
  <mat-label>Name</mat-label>
  <input matInput [formField]="myForm.name" />
  @if (myForm.name().invalid() && myForm.name().touched()) {
    @for (error of myForm.name().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

### 5. Handle Form Submission

```typescript
protected onSubmit(): void {
  if (this.myForm().valid()) {
    this.dialogRef.close(this.formModel());
  }
}
```

### 6. Verify Build

```bash
nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20
```

## Key Rules

### Form Model
1. **Interface first**: Always define a TypeScript interface for the form model
2. **Signal wrapper**: Wrap the model in `signal<T>()`
3. **Initial values**: Provide sensible defaults in the signal initialization
4. **Nullable fields**: Use `string | null` for optional fields

### Validation
5. **Schema validators**: Use `required()`, `email()`, `minLength()`, etc. from `@angular/forms/signals`
6. **English messages**: All validation messages MUST be in English
7. **Multiple validators**: Chain multiple validators for the same field

### Template Binding
8. **[formField] directive**: Use `[formField]="myForm.fieldName"` for binding
9. **Field state signals**: Access state via `myForm.fieldName().valid()`, `.touched()`, `.errors()`
10. **Error display**: Use `@if` with `invalid()` AND `touched()` conditions

### Form State
11. **Form validity**: Use `myForm().valid()` directly in template or component
12. **No isFormValid computed**: Do NOT create separate `isFormValid = computed(() => ...)` - use `myForm().valid()` directly
13. **Computed signals**: Use `computed()` to derive state from form model - no subscriptions

### Button Rules (CRITICAL)
14. **Button styling**: All buttons use bare `matButton` (no value) with CSS classes for color:
    - `class="btn-action"` - Submit/Save buttons (yellow, primary action)
    - `class="btn-cancel"` - Cancel/Back buttons (gray, secondary action)
    - See `/frontend-design-system` for full button type and color class guide
15. **Loading button**: ALL async buttons MUST use `sharedLoadingButton` directive with `(loadingClick)`
16. **Icons required**: ALL buttons MUST have icon-only OR icon with text (text-only buttons prohibited)
17. **No canSubmit computed**: Do NOT create `canSubmit = computed(() => form().valid() && !isSubmitting())` - use `[disabled]="!myForm().valid()"` and let directive handle loading

**Standard dialog actions pattern:**
```html
<mat-dialog-actions align="end">
  <button matButton class="btn-cancel" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    Cancel
  </button>
  <button matButton class="btn-action" type="button" [disabled]="!myForm().valid()" (click)="onSubmit()">
    <mat-icon>save</mat-icon>
    Save
  </button>
</mat-dialog-actions>
```

### Replacing valueChanges
18. **No subscriptions**: Replace `valueChanges.subscribe()` with `computed()` signals
19. **Form model IS reactive**: Reading `formModel()` in a `computed()` automatically reacts to changes

## Available Validators

```typescript
import { required, email, minLength, maxLength, min, max, pattern } from '@angular/forms/signals';

// Usage in form() second parameter
protected readonly myForm = form(this.formModel, (f) => {
  required(f.email, { message: 'Email is required' });
  email(f.email, { message: 'Invalid email address' });
  minLength(f.password, 8, { message: 'Password must be at least 8 characters' });
  maxLength(f.name, 100, { message: 'Name must be at most 100 characters' });
  min(f.amount, 0, { message: 'Amount must be positive' });
  max(f.amount, 1000000, { message: 'Amount is too large' });
  pattern(f.code, /^[A-Z0-9]+$/, { message: 'Code may only contain uppercase letters and numbers' });
});
```

## Common Form Scenarios

### Text Input
```html
<mat-form-field appearance="outline">
  <mat-label>Name</mat-label>
  <input matInput [formField]="myForm.name" />
  @if (myForm.name().invalid() && myForm.name().touched()) {
    @for (error of myForm.name().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

### Select Dropdown
```html
<mat-form-field appearance="outline">
  <mat-label>Category</mat-label>
  <mat-select [formField]="myForm.categoryId">
    @for (category of categories(); track category.id) {
      <mat-option [value]="category.id">{{ category.name }}</mat-option>
    }
  </mat-select>
  @if (myForm.categoryId().invalid() && myForm.categoryId().touched()) {
    @for (error of myForm.categoryId().errors(); track error.kind) {
      <mat-error>{{ error.message }}</mat-error>
    }
  }
</mat-form-field>
```

### Checkbox
```html
<mat-checkbox [formField]="myForm.isActive">Active</mat-checkbox>
```

### Date Picker
```html
<mat-form-field appearance="outline">
  <mat-label>Date</mat-label>
  <input matInput [matDatepicker]="picker" [formField]="myForm.date" />
  <mat-datepicker-toggle matIconSuffix [for]="picker"></mat-datepicker-toggle>
  <mat-datepicker #picker></mat-datepicker>
</mat-form-field>
```

### Autocomplete
```html
<mat-form-field appearance="outline">
  <mat-label>Vendor</mat-label>
  <input matInput [formField]="myForm.vendor" [matAutocomplete]="vendorAuto" />
  <mat-autocomplete #vendorAuto="matAutocomplete">
    @for (option of filteredVendors(); track option) {
      <mat-option [value]="option">{{ option }}</mat-option>
    }
  </mat-autocomplete>
</mat-form-field>
```

## Templates

See `references/` folder for:

- `signal-form-dialog-template.md` - Dialog form pattern (Pattern 1)
- `signal-form-component-template.md` - Route component form patterns (Pattern 4, 5, 6)
- `signal-form-patterns.md` - Validation, button styling, and valueChanges replacement patterns
