"""Skill sync logic -- copies skill files to the target project."""

from __future__ import annotations

import shutil
from pathlib import Path

from rich.console import Console

from ana-skills.models import AgentFramework, AGENT_SKILL_PATHS
from ana-skills.resources import (
    find_skill_family,
    get_skill_dir,
    parse_skill_frontmatter,
)

console = Console()


def _wrap_frontmatter(
    framework: AgentFramework,
    name: str,
    description: str,
    body: str,
) -> str:
    """Wrap skill body with framework-specific YAML frontmatter."""
    if framework == AgentFramework.CURSOR:
        return (
            f"---\nname: {name}\ndescription: {description}\n"
            f"globs: []\nalwaysApply: false\n---\n\n{body}\n"
        )
    return f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n"


def _copy_subdir(src_dir: Path, dest_dir: Path, subdir_name: str) -> None:
    """Copy a subdirectory (references/, scripts/) if it exists."""
    src = src_dir / subdir_name
    if not src.exists() or not any(src.iterdir()):
        return
    dest = dest_dir / subdir_name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def sync_skill(
    skill_name: str,
    project_root: Path,
    framework: AgentFramework,
) -> None:
    """Sync a single skill to the target project."""
    family = find_skill_family(skill_name)
    if family is None:
        console.print(f"  [yellow]Skill '{skill_name}' not found, skipping[/yellow]")
        return

    skill_dir = get_skill_dir(family, skill_name)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    raw = skill_md.read_text(encoding="utf-8")
    meta, body = parse_skill_frontmatter(raw)
    name = meta.get("name", skill_name)
    description = meta.get("description", "")

    skill_base = project_root / AGENT_SKILL_PATHS[framework]

    if framework == AgentFramework.CLAUDE:
        dest = skill_base / name
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SKILL.md").write_text(
            _wrap_frontmatter(framework, name, description, body),
            encoding="utf-8",
        )
        _copy_subdir(skill_dir, dest, "references")
        _copy_subdir(skill_dir, dest, "scripts")

    elif framework == AgentFramework.COPILOT:
        dest = skill_base / name
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "SKILL.md").write_text(
            _wrap_frontmatter(framework, name, description, body),
            encoding="utf-8",
        )
        _copy_subdir(skill_dir, dest, "references")
        _copy_subdir(skill_dir, dest, "scripts")

    elif framework == AgentFramework.CURSOR:
        skill_base.mkdir(parents=True, exist_ok=True)
        (skill_base / f"{name}.md").write_text(
            _wrap_frontmatter(framework, name, description, body),
            encoding="utf-8",
        )


def sync_skills(
    skill_names: list[str],
    project_root: Path,
    framework: AgentFramework,
) -> int:
    """Sync multiple skills. Returns count of synced skills."""
    count = 0
    for skill_name in skill_names:
        sync_skill(skill_name, project_root, framework)
        count += 1
    return count
