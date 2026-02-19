"""Core models and constants for ana-skills."""

from __future__ import annotations

from enum import Enum


CONFIG_FILE = ".ana-skills.yml"


class AgentFramework(str, Enum):
    """Supported agent environments."""

    CLAUDE = "claude"
    CURSOR = "cursor"
    COPILOT = "copilot"


AGENT_SKILL_PATHS: dict[AgentFramework, str] = {
    AgentFramework.CLAUDE: ".claude/skills",
    AgentFramework.CURSOR: ".cursor/rules",
    AgentFramework.COPILOT: ".github/skills",
}