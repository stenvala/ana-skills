---
name: frontend-dialog
description: Create Angular Material dialog components with static open pattern
---

# Frontend Dialog Creation

Create Angular Material dialog components following the static open pattern with typed interfaces.

## When to Use

- Creating modal dialogs for forms (create/edit)
- Complex interactions that need to return data
- Multi-step wizards in a modal
- Confirmation dialogs with custom content

## Prerequisites

1. Feature module/structure exists
2. Required services available for business logic

## File Location

`src/ui/src/app/features/<feature>/components/<feature>-dialog-<name>/<feature>-dialog-<name>.component.ts`

## Naming Convention

- **Component class**: `<Feature>Dialog<Name>Component` (e.g., `AccountingDialogEditBankAccountComponent`)
- **Selector**: `<feature>-dialog-<name>` (e.g., `accounting-dialog-edit-bank-account`)
- **Input interface**: `<Feature>Dialog<Name>InputData`
- **Output interface**: `<Feature>Dialog<Name>OutputData`
- **Folder**: `<feature>-dialog-<name>/`

## Instructions

### 1. Scaffold Dialog Component

Run the init script to create the file structure:

```bash
python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>
```

Example:
```bash
python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account
```

This generates:
- `src/ui/src/app/features/<feature>/components/<feature>-dialog-<name>/<feature>-dialog-<name>.component.ts`
- `src/ui/src/app/features/<feature>/components/<feature>-dialog-<name>/<feature>-dialog-<name>.component.html`

The generated skeleton uses Pattern B (service call inside dialog). See `references/dialog-template.md` for the complete pattern reference.

### 2. Complete the Component

Fill in the generated TODOs:
- Define InputData and OutputData interfaces
- Define FormModel interface and form fields
- Add validators to `form()`
- Inject your feature service and `SharedNotificationService`
- Implement save logic in `onSubmit` (Pattern B)
- Add form fields to HTML template

### 3. Export from Feature Index

Add export to `src/ui/src/app/features/<feature>/components/index.ts`

### 4. Verify Build

```bash
nvm use 20.19.2 && cd src/ui && ng build --configuration=development 2>&1 | head -20
```

## Key Rules

### Interface Definitions
1. **Always define both interfaces**: Even if one is empty, define `InputData` and `OutputData`
2. **Input interface**: Contains all data needed to initialize the dialog
3. **Output interface**: Contains the result data when dialog is confirmed
4. **undefined return**: Dialog returns `undefined` when cancelled

### Static Open Method
5. **Static method signature**: `static async open(dialog: MatDialog, data: InputData): Promise<OutputData | undefined>`
6. **Use firstValueFrom**: Convert `afterClosed()` observable to promise
7. **Dialog config**: Pass width, position, and other config in the open method

### Component Structure
8. **OnPush change detection**: Always use `ChangeDetectionStrategy.OnPush`
9. **Inject dependencies**: Use `inject()` for `MatDialogRef`, `MAT_DIALOG_DATA`, and services
10. **Protected data**: Mark injected data as `protected` for template access

### Close Behavior
11. **Cancel returns undefined**: Call `dialogRef.close()` without arguments
12. **Submit returns data**: Call `dialogRef.close(outputData)` with typed result
13. **Validate before close**: Only close with data after form validation passes

### Module Imports
14. **Use shared modules**: Always import `[CoreModule, MaterialModule, SharedModule, FormField]` for form dialogs or `[CoreModule, MaterialModule, SharedModule]` for simple dialogs — never import Mat\* modules individually
15. **Dialog DI imports**: Import `MAT_DIALOG_DATA`, `MatDialogRef`, `MatDialog` as TypeScript value imports for dependency injection (not as module imports)

### Form Dialogs
**IMPORTANT**: For dialogs with forms, use the `/frontend-forms` skill instead. That skill provides signal-based forms patterns with proper validation, button styling, and loading states.

## Templates

See `references/` folder for:

- `dialog-template.md` - Dialog component pattern with forms
