"""Skill discovery from the bundled skills directory."""

from __future__ import annotations

from pathlib import Path


# In installed mode, skills are at ana_skills/skills/ (via hatchling force-include).
# In dev mode, skills are at the repo root skills/ directory.
_pkg_skills = Path(__file__).parent / "skills"
_repo_skills = Path(__file__).parent.parent / "skills"
SKILLS_DIR = _pkg_skills if _pkg_skills.exists() else _repo_skills


def list_families() -> list[str]:
    """Return sorted list of skill family names (top-level dirs under skills/)."""
    if not SKILLS_DIR.exists():
        return []
    return sorted(
        d.name
        for d in SKILLS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def list_skills_in_family(family: str) -> list[str]:
    """Return sorted list of skill names within a family."""
    family_dir = SKILLS_DIR / family
    if not family_dir.exists():
        return []
    return sorted(
        d.name
        for d in family_dir.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )


def list_all_skills() -> dict[str, list[str]]:
    """Return all skills organized by family: {family: [skill_name, ...]}."""
    result: dict[str, list[str]] = {}
    for family in list_families():
        skills = list_skills_in_family(family)
        if skills:
            result[family] = skills
    return result


def get_skill_dir(family: str, skill_name: str) -> Path:
    """Return the path to a skill's directory."""
    return SKILLS_DIR / family / skill_name


def get_all_skill_names() -> set[str]:
    """Return a flat set of all skill names across all families."""
    names: set[str] = set()
    for family in list_families():
        names.update(list_skills_in_family(family))
    return names


def find_skill_family(skill_name: str) -> str | None:
    """Find which family a skill belongs to."""
    for family in list_families():
        if skill_name in list_skills_in_family(family):
            return family
    return None


def parse_skill_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from a skill file.

    Returns (metadata_dict, body).
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    metadata: dict[str, str] = {}
    for line in parts[1].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    return metadata, parts[2].lstrip("\n")
