# ana-skills

Portable AI agent skills for Claude Code, Cursor, and GitHub Copilot.

## Philosophy

ana-skills is a **skill library and sync tool** that packages development knowledge -- templates, workflows, conventions, and scripts -- into portable **skills** that work across AI agent environments. Instead of repeating instructions or maintaining separate rule files per editor, you define skills once and sync them wherever they're needed.

Each skill is a self-contained package with:
- **Instructions** (SKILL.md) -- what to do and when
- **References** -- templates, patterns, and examples loaded into context
- **Scripts** -- deterministic automation (scaffolding, validation)

Skills cover the full stack: Angular components, Python services, database models, testing, CI/CD, and more. You pick what matches your project and ana-skills handles the rest.

## Installation

1. Clone ana-skills into your project root:

```bash
git clone https://github.com/stenvala/ana-skills.git ana-skills-package
```

2. Add the following to your project's `pyproject.toml`:

```toml
# Add ana-skills to your dependencies
[project]
dependencies = [
    # ... your other dependencies ...
    "ana-skills",
]

# Register ana-skills-package as a workspace member
[tool.uv.workspace]
members = ["ana-skills-package"]

# Point the ana-skills dependency to the local workspace package
[tool.uv.sources]
ana-skills = { workspace = true }
```

3. Install dependencies:

```bash
uv sync
```

## Setup

```bash
# Interactive setup: choose your agent framework and select skills
uv run ana_skills sync
```

On first run, `sync` walks you through:
1. **Agent selection** -- Claude Code, Cursor, or GitHub Copilot
2. **Skill selection** -- browse by category, pick all or individual skills
3. **Sync** -- copies selected skills to the correct location for your agent

Configuration is saved to `.ana-skills.yml` in your project root.

## Usage

### Sync skills

```bash
# Re-sync all enabled skills (also detects newly added skills)
uv run ana_skills sync
```

Run `sync` after updating ana-skills to pick up new or changed skills. If new skills have been added to the library, you'll be prompted to enable them.

### Manage skills

```bash
# Interactively enable/disable skills
uv run ana_skills add
```

Shows all available skills grouped by category with their current status. Toggle skills on or off -- newly enabled skills are synced immediately.

## Supported Agent Frameworks

| Framework | Skills Location | Commands Location |
|-----------|----------------|-------------------|
| Claude Code | `.claude/skills/` | `.claude/commands/` |
| Cursor | `.cursor/rules/` | `.cursor/commands/` |
| GitHub Copilot | `.github/skills/` | `.github/prompts/` |

## Skill Library

| Category | Skills | Purpose |
|----------|--------|---------|
| **Angular** | `frontend-component`, `frontend-dialog`, `frontend-forms`, `frontend-service`, `frontend-store` | UI components, dialogs, forms, services, state management |
| **Python** | `backend-router`, `backend-service` | API routing, service layer |
| **Database** | `database-design`, `database-model`, `database-repository`, `database-schema-edit-postgres`, `database-schema-edit-sqlite`, `database-setup-postgres`, `database-setup-sqlite` | Schema design, ORM models, repositories, migrations |
| **Testing** | `test-playwright`, `test-python-integration`, `test-python-unit` | E2E, integration, and unit testing |
| **Infrastructure** | `create-web-app`, `mcc-ci-cd` | Project scaffolding, CI/CD pipelines |
| **Common** | `commit`, `code-simplifier`, `skill-creator` | Git conventions, refactoring, creating new skills |

## Skill Structure

Each skill lives under `skills/<category>/<skill-name>/`:

```
skills/angular/frontend-component/
  SKILL.md                              # Instructions and guidelines
  references/                           # Templates and patterns (loaded into context)
    presentational-component-template.md
    route-component-template.md
    ...
  scripts/                              # Automation scripts
    init_frontend_component.py
    init_frontend_route.py
```

### SKILL.md format

```markdown
---
name: skill-name
description: |
  What this skill does.
  When to use it.
---

# Skill Title

Detailed instructions, workflows, and guidelines...
```

The YAML frontmatter (`name`, `description`) drives skill discovery and selection. The markdown body contains the actual instructions your AI agent follows.

## Configuration

Project configuration is stored in `.ana-skills.yml`:

```yaml
agent: claude
skills:
  frontend-component: true
  backend-service: true
  database-model: false
  commit: true
```

- `agent` -- target framework (`claude`, `cursor`, or `copilot`)
- `skills` -- each skill mapped to enabled (`true`) or disabled (`false`)

## Creating Custom Skills

Use the bundled `skill-creator` skill to create new skills that match your project's conventions:

```
/skill-creator
```

Or manually create a new directory under `skills/<category>/<skill-name>/` with a `SKILL.md` file following the frontmatter format above.
