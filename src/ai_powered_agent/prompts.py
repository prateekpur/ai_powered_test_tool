from pathlib import Path

from ai_powered_agent.models import Requirement

PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt_template(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8").strip()


def analyze_requirement(requirement: Requirement) -> str:
    template = _load_prompt_template("analyse_prompt.txt")
    return f"{template}\n\n{requirement.to_markdown()}"
