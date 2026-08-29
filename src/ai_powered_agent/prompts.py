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


def generate_negative_tests(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    scenarios: str = "",
    test_cases: str = "",
) -> str:
    template = _load_prompt_template("generate_negative_tests_prompt.txt")
    sections = [
        f"{template}\n",
        f"## Requirement\n\n{requirement.to_markdown()}",
        f"## Analysis\n\n{analysis.to_markdown()}",
    ]
    if scenarios.strip():
        sections.append(f"## Existing Test Scenarios\n\n{scenarios.strip()}")
    if test_cases.strip():
        sections.append(f"## Existing Test Cases\n\n{test_cases.strip()}")
    return "\n\n".join(sections)


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


def remediate_coverage_gaps(
    requirement: Requirement,
    analysis: RequirementAnalysis,
    scenarios: str,
    test_cases: str,
    coverage_gaps: str,
    negative_tests: str = "",
    security_tests: str = "",
) -> str:
    template = _load_prompt_template("remediate_gaps_prompt.txt")
    sections = [
        f"{template}\n",
        f"## Requirement\n\n{requirement.to_markdown()}",
        f"## Analysis\n\n{analysis.to_markdown()}",
        f"## Existing Test Scenarios\n\n{scenarios.strip()}",
        f"## Existing Test Cases\n\n{test_cases.strip()}",
        f"## Coverage/Traceability Validation\n\n{coverage_gaps.strip()}",
    ]
    if negative_tests.strip():
        sections.append(f"## Existing Negative Tests\n\n{negative_tests.strip()}")
    if security_tests.strip():
        sections.append(f"## Existing Security Tests\n\n{security_tests.strip()}")
    return "\n\n".join(sections)


def validate_test_schema(
    scenarios: str,
    test_cases: str,
    negative_tests: str = "",
) -> str:
    template = _load_prompt_template("schema_validation_prompt.txt")
    sections = [
        f"{template}\n",
        f"## Test Scenarios\n\n{scenarios.strip()}",
        f"## Test Cases\n\n{test_cases.strip()}",
    ]
    if negative_tests.strip():
        negative_template = _load_prompt_template("validate_negative_tests_prompt.txt")
        sections.append(f"{negative_template}\n\n## Negative Tests\n\n{negative_tests.strip()}")
    return "\n\n".join(sections)
