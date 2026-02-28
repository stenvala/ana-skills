# Build Patterns (`mcc_build.py`)

## Overview

The build script (`mcc_build.py`) runs in the project root on the CI server (or locally on macOS for testing). It produces an `output/` directory containing everything needed for deployment. **Only contents of `output/` are transferred to the remote server.**

The MCC pipeline invokes the build script as: `uv run mcc_build.py --link-mode=copy`. The `--link-mode=copy` is a `uv` flag (not passed to the script) that tells `uv` to copy packages instead of symlinking them, which is required for the build output to be portable across machines.

## Execution Order

1. Clean `output/` directory
2. Run tests and quality checks (fail-fast)
3. Build frontend (if applicable)
4. Copy backend source to `output/`
5. Copy deployment configs to `output/`
6. Copy deployment scripts and supporting files to `output/`

## Critical Rule: Output Directory Boundary

Everything the deploy script needs must be in `output/`. This includes:

- `mcc_deploy.py` itself
- `mcc_common.py`
- Any stage-specific conf files (`conf-prod.yml`, `conf-dev.yml`)
- `config.yml` (stage routing)
- `build_info.yml` (added by pipeline service, copy it to output)
- `pyproject.toml` + `uv.lock` (for remote venv sync)
- Any migration scripts, seed scripts, backup scripts
- Any additional deploy-time scripts (e.g., `mcc_clone.py`)

## Example: Full-Stack Python/Angular Project

```python
"""Build script for MyApp."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from mcc_common import run

PROJECT_DIR = Path(__file__).parent.absolute()
OUTPUT_DIR = PROJECT_DIR / "output"

# Node.js path handling (macOS dev vs Linux CI)
NODE_ENV = os.environ.copy()
if sys.platform != "darwin":
    NODE_ENV["PATH"] = "/home/stenvala/.nvm/versions/node/v20.19.2/bin:" + NODE_ENV["PATH"]
NPM = "npm" if sys.platform == "darwin" else "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npm"
NPX = "npx" if sys.platform == "darwin" else "/home/stenvala/.nvm/versions/node/v20.19.2/bin/npx"


def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_tests()
    build_ui()
    copy_api()
    copy_deploy_files()


def run_tests():
    """Run tests first. Build fails if tests fail."""
    print("Running tests...", flush=True)
    run(["uv", "run", "python", "run_tests.py", "all", "-cv"], cwd=PROJECT_DIR)
    print("All tests passed", flush=True)


def build_ui():
    """Build Angular UI and copy to output."""
    ui_dir = PROJECT_DIR / "src" / "ui"
    if not (ui_dir / "node_modules").exists():
        run([NPM, "ci"], cwd=ui_dir, env=NODE_ENV)
    run([NPX, "ng", "build", "--configuration=production"], cwd=ui_dir, env=NODE_ENV)
    browser_dir = ui_dir / "dist" / "app-name" / "browser"
    shutil.copytree(browser_dir, OUTPUT_DIR / "ui")


def copy_api():
    """Copy backend source to output."""
    shutil.copytree(PROJECT_DIR / "src" / "api", OUTPUT_DIR / "api")
    shutil.copytree(PROJECT_DIR / "src" / "shared", OUTPUT_DIR / "shared")


def copy_deploy_files():
    """Copy everything needed for deployment."""
    # Individual files
    for filename in [
        "pyproject.toml", "uv.lock", "config.yml", "build_info.yml",
        "mcc_deploy.py", "mcc_common.py",
    ]:
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / filename)

    # Stage conf files from mcc/ directory
    for conf_name in ("conf-prod.yml", "conf-dev.yml"):
        conf_src = PROJECT_DIR / "mcc" / conf_name
        if conf_src.exists():
            shutil.copy2(conf_src, OUTPUT_DIR / conf_name)


if __name__ == "__main__":
    try:
        print("Starting build", flush=True)
        main()
        print("Build finished", flush=True)
    except Exception as e:
        print(f"Build failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
```

## Example: API-Only Python Project (No Frontend)

```python
def main():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    run_tests()
    copy_api()
    copy_migrations()
    copy_deploy_files()


def copy_migrations():
    """Copy database migration files to output."""
    migrations_dir = PROJECT_DIR / "migrations"
    if migrations_dir.exists():
        shutil.copytree(migrations_dir, OUTPUT_DIR / "migrations")
```

## Example: Project with Worker Process

```python
def copy_deploy_files():
    """Copy deploy files including worker code."""
    for filename in [
        "pyproject.toml", "uv.lock", "config.yml", "build_info.yml",
        "mcc_deploy.py", "mcc_common.py",
    ]:
        src = PROJECT_DIR / filename
        if src.exists():
            shutil.copy2(src, OUTPUT_DIR / filename)

    # Worker source
    shutil.copytree(PROJECT_DIR / "src" / "worker", OUTPUT_DIR / "worker")
```

## Adapting to Your Project

Key decisions when creating `mcc_build.py`:

| Concern                  | Options                                                   |
| ------------------------ | --------------------------------------------------------- |
| **Testing**              | `uv run run_tests.py`, custom test runner                 |
| **Frontend**             | Angular (`npx ng build`)                                  |
| **Backend**              | Single `api/` dir, `api/` + `shared/`, multiple modules   |
| **Migrations**           | SQL files in `migrations/`, Alembic directory, none       |
| **Extra scripts**        | Backup scripts, cron scripts, seed scripts                |
| **Extra deploy scripts** | `mcc_clone.py` or similar non-deployment stage scripts    |
| **Domain configs**       | Per-domain config.yml files (multi-tenant), single config |
