"""CLI entry point for ana-skills."""

import typer

from ana_skills.commands.sync_cmd import sync_command

app = typer.Typer(
    name="ana-skills",
    help="Sync agent skills to projects.",
    no_args_is_help=True,
)

app.command("sync")(sync_command)


if __name__ == "__main__":
    app()
