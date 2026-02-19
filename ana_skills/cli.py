"""CLI entry point for ana_skills."""

import typer

from ana_skills.commands.sync_cmd import download_command
from ana_skills.commands.upload_cmd import upload_command

app = typer.Typer(
    name="ana_skills",
    help="Sync agent skills between packages and projects.",
    no_args_is_help=True,
)

app.command("download")(download_command)
app.command("upload")(upload_command)


if __name__ == "__main__":
    app()
