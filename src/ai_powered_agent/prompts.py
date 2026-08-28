from pathlib import Path

from ai_powered_agent.models import Requirement, RequirementAnalysis

PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt_template(name: str) -> str:
    path = PROMPT_DIR / name
    return path.read_text(encoding="utf-8").strip()


def analyze_requirement(requirement: Requirement) -> str:
    template = _load_prompt_template("analyse_prompt.txt")
    return f"{template}\n\n{requirement.to_markdown()}"


def generate_test_scenarios(requirement: Requirement, analysis: RequirementAnalysis) -> str:
    template = _load_prompt_template("generate_scenarios_prompt.txt")
    return (
        f"{template}\n\n"
        f"## Requirement\n\n{requirement.to_markdown()}\n\n"
        f"## Analysis\n\n{analysis.to_markdown()}"
    )

def generate_test_cases(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    scenarios: str,
) -> str:
    template = _load_prompt_template("generate_test_cases_prompt.txt")
    return (
        f"{template}\n\n"
        f"## Requirement\n\n{requirement.to_markdown()}\n\n"
        f"## Analysis\n\n{analysis.to_markdown()}\n\n"
        f"## Test Scenarios\n\n{scenarios.strip()}"
    )


def validate_coverage_traceability(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    scenarios: str,
    test_cases: str,
    negative_tests: str = "",
    security_tests: str = "",
) -> str:
    template = _load_prompt_template("coverage_traceability_validator_prompt.txt")
    sections = [
        f"{template}\n",
        f"## Requirement\n\n{requirement.to_markdown()}",
        f"## Analysis\n\n{analysis.to_markdown()}",
        f"## Test Scenarios\n\n{scenarios.strip()}",
        f"## Test Cases\n\n{test_cases.strip()}",
    ]
    if negative_tests.strip():
        sections.append(f"## Negative Tests\n\n{negative_tests.strip()}")
    if security_tests.strip():
        sections.append(f"## Security Tests\n\n{security_tests.strip()}")
    return "\n\n".join(sections)
