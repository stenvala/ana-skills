#!/usr/bin/env python3
"""
Initialize a dummy Angular dialog component with signal-based forms.

Usage:
    python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>

Example:
    python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account

This creates:
    src/ui/src/app/features/accounting/components/accounting-dialog-edit-bank-account/
        accounting-dialog-edit-bank-account.component.ts
        accounting-dialog-edit-bank-account.component.html
"""

import os
import sys
from pathlib import Path


def to_pascal_case(kebab_name: str) -> str:
    """Convert kebab-case to PascalCase."""
    return "".join(word.capitalize() for word in kebab_name.split("-"))


def create_dialog_component(feature: str, dialog_name: str):
    """Create a dialog component with minimal skeleton."""

    feature_pascal = to_pascal_case(feature)
    dialog_pascal = to_pascal_case(dialog_name)

    # Full component name: AccountingDialogEditBankAccount
    component_name = f"{feature_pascal}Dialog{dialog_pascal}Component"
    selector = f"{feature}-dialog-{dialog_name}"
    folder_name = f"{feature}-dialog-{dialog_name}"

    # Paths
    base_path = Path("src/ui/src/app/features") / feature / "components" / folder_name
    ts_file = base_path / f"{folder_name}.component.ts"
    html_file = base_path / f"{folder_name}.component.html"

    # Create directory
    base_path.mkdir(parents=True, exist_ok=True)

    # TypeScript content
    ts_content = f'''import {{ Component, ChangeDetectionStrategy, inject, signal, effect, untracked }} from '@angular/core';
import {{ form, FormField, required, maxLength }} from '@angular/forms/signals';
import {{ MAT_DIALOG_DATA, MatDialogRef, MatDialogModule, MatDialog }} from '@angular/material/dialog';
import {{ MatFormFieldModule }} from '@angular/material/form-field';
import {{ MatInputModule }} from '@angular/material/input';
import {{ MatButtonModule }} from '@angular/material/button';
import {{ MatIconModule }} from '@angular/material/icon';
import {{ firstValueFrom }} from 'rxjs';

export interface {feature_pascal}Dialog{dialog_pascal}InputData {{
  // TODO: Define input fields
  isEdit: boolean;
}}

export interface {feature_pascal}Dialog{dialog_pascal}OutputData {{
  // TODO: Define output fields
}}

interface {dialog_pascal}FormModel {{
  // TODO: Define form fields
}}

@Component({{
  selector: '{selector}',
  imports: [
    FormField,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './{folder_name}.component.html',
}})
export class {component_name} {{
  private readonly dialogRef = inject(MatDialogRef<{component_name}>);
  protected readonly data = inject<{feature_pascal}Dialog{dialog_pascal}InputData>(MAT_DIALOG_DATA);

  private readonly formModel = signal<{dialog_pascal}FormModel>({{
    // TODO: Initialize form fields
  }});

  protected readonly {dialog_name.replace('-', '')}Form = form(this.formModel, (f) => {{
    // TODO: Add validators
  }});

  constructor() {{
    // Initialize form with input data
    effect(() => {{
      const data = this.data;
      untracked(() => {{
        this.formModel.set({{
          // TODO: Map input data to form model
        }});
      }});
    }});
  }}

  protected onCancel(): void {{
    this.dialogRef.close();
  }}

  protected onSubmit(): void {{
    if (this.{dialog_name.replace('-', '')}Form().valid()) {{
      this.dialogRef.close(this.formModel() as {feature_pascal}Dialog{dialog_pascal}OutputData);
    }}
  }}

  static async open(
    dialog: MatDialog,
    data: {feature_pascal}Dialog{dialog_pascal}InputData
  ): Promise<{feature_pascal}Dialog{dialog_pascal}OutputData | undefined> {{
    return await firstValueFrom(
      dialog
        .open({component_name}, {{
          data,
          width: '', // TODO: Set width (e.g., '400px', '500px')
          disableClose: true,
        }})
        .afterClosed()
    );
  }}
}}
'''

    # HTML content
    html_content = f'''<h2 mat-dialog-title>{{{{ data.isEdit ? 'Muokkaa' : 'Lisää uusi' }}}}</h2>

<mat-dialog-content>
  <!-- TODO: Add form fields -->
</mat-dialog-content>

<mat-dialog-actions align="end">
  <button matButton="outlined" type="button" (click)="onCancel()">
    <mat-icon>close</mat-icon>
    Peruuta
  </button>
  <button matButton="filled" type="button" [disabled]="!{dialog_name.replace('-', '')}Form().valid()" (click)="onSubmit()">
    <mat-icon>save</mat-icon>
    Tallenna
  </button>
</mat-dialog-actions>
'''

    # Write files
    ts_file.write_text(ts_content)
    html_file.write_text(html_content)

    print(f"Created dialog component:")
    print(f"  {ts_file}")
    print(f"  {html_file}")
    print()
    print(f"Component: {component_name}")
    print(f"Selector: {selector}")
    print()
    print("TODO:")
    print("  1. Define InputData and OutputData interfaces")
    print("  2. Define FormModel interface")
    print("  3. Add validators to form()")
    print("  4. Set dialog width in open() method")
    print("  5. Add form fields to HTML template")
    print("  6. Export from feature's components/index.ts")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py <feature> <dialog-name>")
        print("Example: python .claude/skills/frontend-dialog/scripts/init_frontend_dialog.py accounting edit-bank-account")
        sys.exit(1)

    feature = sys.argv[1]
    dialog_name = sys.argv[2]

    create_dialog_component(feature, dialog_name)
