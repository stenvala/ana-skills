"""ana_skills upload -- upload skills from the project back to the package."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ana_skills.config import config_exists, get_agent, load_config
from ana_skills.models import AGENT_SKILL_PATHS, AgentFramework
from ana_skills.resources import (
    SKILLS_DIR,
    find_skill_family,
    get_all_skill_names,
    get_skill_dir,
    list_families,
)

console = Console()


def _list_project_skills(project_root: Path, framework: AgentFramework) -> list[str]:
    """List all skill names found in the project's agent skills directory."""
    skill_base = project_root / AGENT_SKILL_PATHS[framework]
    if not skill_base.exists():
        return []

    if framework == AgentFramework.CURSOR:
        # Cursor uses flat .md files
        return sorted(p.stem for p in skill_base.glob("*.md"))

    # Claude and Copilot use directories with SKILL.md inside
    return sorted(
        d.name
        for d in skill_base.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )


def _upload_skill(
    skill_name: str,
    project_root: Path,
    framework: AgentFramework,
    family: str,
) -> None:
    """Upload a single skill from the project back to the package."""
    skill_base = project_root / AGENT_SKILL_PATHS[framework]

    if framework == AgentFramework.CURSOR:
        src_file = skill_base / f"{skill_name}.md"
        if not src_file.exists():
            console.print(f"  [yellow]Skill '{skill_name}' not found in project, skipping[/yellow]")
            return
        dest_dir = SKILLS_DIR / family / skill_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        # For Cursor, strip the extra globs/alwaysApply from frontmatter
        content = src_file.read_text(encoding="utf-8")
        (dest_dir / "SKILL.md").write_text(content, encoding="utf-8")
    else:
        # Claude and Copilot use directories
        src_dir = skill_base / skill_name
        if not src_dir.exists():
            console.print(f"  [yellow]Skill '{skill_name}' not found in project, skipping[/yellow]")
            return

        dest_dir = SKILLS_DIR / family / skill_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy SKILL.md
        src_md = src_dir / "SKILL.md"
        if src_md.exists():
            (dest_dir / "SKILL.md").write_text(
                src_md.read_text(encoding="utf-8"), encoding="utf-8"
            )

        # Copy subdirectories (references/, scripts/)
        for subdir_name in ("references", "scripts"):
            src_sub = src_dir / subdir_name
            if src_sub.exists() and any(src_sub.iterdir()):
                dest_sub = dest_dir / subdir_name
                if dest_sub.exists():
                    shutil.rmtree(dest_sub)
                shutil.copytree(src_sub, dest_sub)

    console.print(f"  [green]Uploaded[/green] {skill_name} → {family}/{skill_name}")


def _ask_family(skill_name: str) -> str:
    """Ask the user which family to place a new skill in."""
    families = list_families()
    console.print(f"\n[bold]Select a family for new skill '{skill_name}':[/bold]\n")
    for i, family in enumerate(families, 1):
        console.print(f"  {i}) {family}")
    console.print()

    choice = typer.prompt("Enter your choice", default="1")
    try:
        idx = int(choice.strip()) - 1
        if 0 <= idx < len(families):
            return families[idx]
    except ValueError:
        pass

    console.print("[red]Invalid choice. Using first family.[/red]")
    return families[0]


def upload_command(
    skill_name: Optional[str] = typer.Argument(
        None,
        help="Name of a specific skill to upload. If omitted, uploads all existing skills.",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project root directory.",
    ),
) -> None:
    """Upload skills from the project back to the ana-skills package.

    Without arguments, uploads all skills that exist in both the project and
    the package, and reports skills that exist only in the project.

    With a skill name argument, uploads that specific skill (even if new).
    """
    if not config_exists(project_dir):
        console.print(
            "[red]No .ana_skills.yml found. Run 'ana-skills download' first to set up.[/red]"
        )
        raise typer.Exit(1)

    cfg = load_config(project_dir)
    framework = get_agent(cfg)
    if not framework:
        console.print(
            "[red]Invalid agent in .ana_skills.yml. Delete the file and run download again.[/red]"
        )
        raise typer.Exit(1)

    project_skills = _list_project_skills(project_dir, framework)
    package_skills = get_all_skill_names()

    if skill_name:
        # Upload a specific skill
        if skill_name not in project_skills:
            console.print(
                f"[red]Skill '{skill_name}' not found in project at "
                f"{project_dir / AGENT_SKILL_PATHS[framework]}[/red]"
            )
            raise typer.Exit(1)

        family = find_skill_family(skill_name)
        if family is None:
            # New skill - ask for family
            console.print(
                f"[bold yellow]Skill '{skill_name}' is new (not in package).[/bold yellow]"
            )
            family = _ask_family(skill_name)

        _upload_skill(skill_name, project_dir, framework, family)
        console.print("[bold green]Upload complete.[/bold green]")
        return

    # Upload all existing skills
    in_both = sorted(s for s in project_skills if s in package_skills)
    only_in_project = sorted(s for s in project_skills if s not in package_skills)

    if in_both:
        console.print(
            f"\n[bold]Uploading {len(in_both)} skill(s) back to package...[/bold]"
        )
        for name in in_both:
            family = find_skill_family(name)
            if family:
                _upload_skill(name, project_dir, framework, family)
        console.print("[bold green]Upload complete.[/bold green]")
    else:
        console.print("[yellow]No matching skills to upload.[/yellow]")

    if only_in_project:
        console.print(
            f"\n[bold yellow]Skills in project but not in package ({len(only_in_project)}):[/bold yellow]"
        )
        for name in only_in_project:
            console.print(f"  • {name}")
        console.print(
            "\n[dim]To upload a new skill, run: ana-skills upload <skill-name>[/dim]"
        )
