"""ana_skills download -- download skills from package to the target project."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from ana_skills.config import (
    config_exists,
    get_agent,
    get_all_configured_skills,
    get_enabled_skills,
    load_config,
    save_config,
)
from ana_skills.models import AgentFramework
from ana_skills.resources import get_all_skill_names, list_all_skills
from ana_skills.sync import sync_skills

console = Console()


def _ask_agent() -> AgentFramework:
    """Interactively ask the user which agent environment they use."""
    console.print("\n[bold]Select your agent environment:[/bold]\n")
    console.print("  1) Claude Code")
    console.print("  2) Cursor")
    console.print("  3) GitHub Copilot")
    console.print()

    choice = typer.prompt("Enter your choice", default="1")
    mapping = {
        "1": AgentFramework.CLAUDE,
        "2": AgentFramework.CURSOR,
        "3": AgentFramework.COPILOT,
    }
    framework = mapping.get(choice.strip())
    if not framework:
        console.print("[red]Invalid choice. Defaulting to Claude Code.[/red]")
        framework = AgentFramework.CLAUDE
    return framework


def _ask_skills_selection() -> dict[str, bool]:
    """Interactively ask which skills to sync, family by family."""
    all_skills = list_all_skills()
    selections: dict[str, bool] = {}

    console.print("\n[bold]Select skills to sync:[/bold]\n")

    for family, skills in all_skills.items():
        skill_list = ", ".join(skills)
        console.print(f"[cyan]{family}[/cyan] ({skill_list}):")
        console.print("  \\[a] Sync all  \\[n] Skip all  \\[s] Select individually")
        choice = typer.prompt("  Choice", default="a").strip().lower()

        if choice == "a":
            for skill in skills:
                selections[skill] = True
        elif choice == "n":
            for skill in skills:
                selections[skill] = False
        elif choice == "s":
            for skill in skills:
                yn = typer.prompt(f"    {skill} (y/n)", default="y").strip().lower()
                selections[skill] = yn == "y"
        else:
            console.print("  [yellow]Invalid choice, syncing all.[/yellow]")
            for skill in skills:
                selections[skill] = True

        console.print()

    return selections


def _check_new_skills(cfg: dict) -> dict[str, bool] | None:
    """Check for new skills not yet in the config. Returns updates or None."""
    configured = set(get_all_configured_skills(cfg).keys())
    available = get_all_skill_names()
    new_skills = available - configured

    if not new_skills:
        return None

    console.print(
        f"\n[bold yellow]Found {len(new_skills)} new skill(s) not in your config.[/bold yellow]"
    )
    show = (
        typer.prompt("Would you like to review them? (y/n)", default="y")
        .strip()
        .lower()
    )
    if show != "y":
        return None

    updates: dict[str, bool] = {}
    all_skills = list_all_skills()

    # Group new skills by family for nicer display
    for family, skills in all_skills.items():
        family_new = [s for s in skills if s in new_skills]
        if not family_new:
            continue
        console.print(f"\n  [cyan]{family}[/cyan]:")
        for skill in family_new:
            yn = typer.prompt(f"    Add {skill}? (y/n)", default="y").strip().lower()
            updates[skill] = yn == "y"

    return updates


def download_command(
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project root directory.",
    ),
) -> None:
    """Download skills from the package to the project.

    On first run, asks which agent environment and skills to sync.
    On subsequent runs, syncs previously selected skills and offers to add new ones.
    """
    if not config_exists(project_dir):
        # First time setup
        console.print("[bold]ana_skills setup[/bold]")

        framework = _ask_agent()
        selections = _ask_skills_selection()

        cfg = {
            "agent": framework.value,
            "skills": selections,
        }
        save_config(project_dir, cfg)
        console.print(
            f"\nSaved configuration to [cyan]{project_dir / '.ana_skills.yml'}[/cyan]"
        )

        enabled = [name for name, on in selections.items() if on]
        if enabled:
            console.print(f"\nSyncing {len(enabled)} skill(s)...")
            sync_skills(enabled, project_dir, framework)
            console.print("[bold green]Sync complete.[/bold green]")
        else:
            console.print("[yellow]No skills selected. Nothing to sync.[/yellow]")
        return

    # Subsequent run
    cfg = load_config(project_dir)
    framework = get_agent(cfg)
    if not framework:
        console.print(
            "[red]Invalid agent in .ana_skills.yml. Delete the file and run sync again.[/red]"
        )
        raise typer.Exit(1)

    # Check for new skills
    updates = _check_new_skills(cfg)
    if updates:
        skills_section = cfg.get("skills", {})
        skills_section.update(updates)
        cfg["skills"] = skills_section
        save_config(project_dir, cfg)
        newly_added = [name for name, on in updates.items() if on]
        if newly_added:
            console.print(f"\nAdded {len(newly_added)} new skill(s) to config.")

    enabled = get_enabled_skills(cfg)
    if not enabled:
        console.print(
            "[yellow]No skills enabled. Edit .ana_skills.yml to enable skills.[/yellow]"
        )
        return

    console.print(
        f"\nSyncing {len(enabled)} skill(s) to [cyan]{framework.value}[/cyan]..."
    )
    sync_skills(enabled, project_dir, framework)
    console.print("[bold green]Sync complete.[/bold green]")
