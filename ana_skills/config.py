"""Configuration file (.ana-skills.yml) management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ana-skills.models import CONFIG_FILE, AgentFramework


def config_path(project_dir: Path) -> Path:
    """Return the path to the config file."""
    return project_dir / CONFIG_FILE


def config_exists(project_dir: Path) -> bool:
    """Check if the config file exists."""
    return config_path(project_dir).exists()


def load_config(project_dir: Path) -> dict[str, Any]:
    """Load the .ana-skills.yml config. Returns empty dict if missing."""
    path = config_path(project_dir)
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def save_config(project_dir: Path, cfg: dict[str, Any]) -> None:
    """Save config to .ana-skills.yml."""
    path = config_path(project_dir)
    if "skills" in cfg:
        cfg["skills"] = dict(sorted(cfg["skills"].items()))
    path.write_text(yaml.dump(cfg, default_flow_style=False, sort_keys=False), encoding="utf-8")


def get_agent(cfg: dict[str, Any]) -> AgentFramework | None:
    """Get the configured agent framework."""
    agent = cfg.get("agent")
    if agent:
        try:
            return AgentFramework(agent)
        except ValueError:
            return None
    return None


def get_enabled_skills(cfg: dict[str, Any]) -> list[str]:
    """Return list of skill names that are enabled (true)."""
    skills = cfg.get("skills", {})
    return [name for name, enabled in skills.items() if enabled]


def get_all_configured_skills(cfg: dict[str, Any]) -> dict[str, bool]:
    """Return all configured skills with their enabled status."""
    return cfg.get("skills", {})
