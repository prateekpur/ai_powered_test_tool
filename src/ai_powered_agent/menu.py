from pathlib import Path
from typing import Any

from ai_powered_agent.agent import (
    AgentRunError,
    AgentStartupError,
    LLMUnavailableError,
    run_agent,
)
from ai_powered_agent.models import Requirement, RequirementAnalysis, RequirementPriority
from ai_powered_agent import prompts
from ai_powered_agent.session import Session

MENU_OPTIONS = [
    "Analyze Requirement",
    "Generate Test Scenarios",
    "Generate Test Cases",
    "Generate Negative Tests",
    "Generate Security Tests",
    "Coverage/Traceability Validator",
    "Remediate Coverage Gaps",
    "Export Report",
    "Exit",
]


def _read_multiline(label: str) -> str:
    print(label)
    print("(Press Enter on an empty line when done)")
    lines: list[str] = []
    while True:
        line = input()
        if not line and lines:
            break
        lines.append(line)
    return "\n".join(lines).strip()


def _read_requirement() -> Requirement | None:
    title = input("\nTitle: ").strip()
    if not title:
        return None

    description = _read_multiline("Description:")
    if not description:
        return None

    source = input("Source (optional, e.g. JIRA-123): ").strip()
    priority_input = input("Priority [low/medium/high] (default: medium): ").strip().lower()
    try:
        priority = RequirementPriority(priority_input) if priority_input else RequirementPriority.MEDIUM
    except ValueError:
        print("Invalid priority. Using medium.")
        priority = RequirementPriority.MEDIUM

    print("Acceptance criteria (blank line to finish):")
    acceptance_criteria: list[str] = []
    while True:
        item = input("- ").strip()
        if not item:
            break
        acceptance_criteria.append(item)

    return Requirement(
        title=title,
        description=description,
        source=source,
        priority=priority,
        acceptance_criteria=acceptance_criteria,
    )


def _pause() -> None:
    input("\nPress Enter to continue...")


def _require_requirement(session: Session) -> bool:
    if session.requirement is not None:
        return True
    print("Set a requirement first (option 1).")
    _pause()
    return False


def _require_analysis(session: Session) -> bool:
    if not _require_requirement(session):
        return False
    if session.analysis is not None and session.analysis.has_content():
        return True
    print("Run requirement analysis first (option 1).")
    _pause()
    return False


def _require_scenarios(session: Session) -> bool:
    if not _require_analysis(session):
        return False
    if session.test_scenarios.strip():
        return True
    print("Generate test scenarios first (option 2).")
    _pause()
    return False


def _require_test_cases(session: Session) -> bool:
    if not _require_scenarios(session):
        return False
    if session.test_cases.strip():
        return True
    print("Generate test cases first (option 3).")
    _pause()
    return False


def _require_coverage_validation(session: Session) -> bool:
    if not _require_test_cases(session):
        return False
    if session.coverage_traceability.strip():
        return True
    print("Run Coverage/Traceability Validator first (option 6).")
    _pause()
    return False


def _run_action(cwd: Path, prompt: str) -> str | None:
    try:
        return run_agent(prompt, cwd=cwd)
    except LLMUnavailableError as err:
        print(f"\nLLM unavailable: {err}")
        if err.retryable:
            print("This may be temporary. You can try again shortly.")
    except AgentStartupError as err:
        print(f"\nLLM error: {err}")
    except AgentRunError as err:
        print(f"\nLLM run failed: {err}")
    _pause()
    return None


def _build_prompt(name: str, **kwargs: Any) -> str | None:
    builder = getattr(prompts, name, None)
    if not callable(builder):
        print(f"Prompt '{name}' is not configured yet. Add it to prompts.py.")
        _pause()
        return None
    return builder(**kwargs)


def _analyze_requirement(session: Session, cwd: Path) -> None:
    requirement = _read_requirement()
    if requirement is None:
        print("No requirement provided.")
        _pause()
        return

    session.requirement = requirement
    prompt = _build_prompt("analyze_requirement", requirement=requirement)
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.analysis = RequirementAnalysis(
            requirement_id=requirement.id,
            raw_response=result,
        )
        print("\nRequirement analysis saved to session.")
        _pause()


def _generate_test_scenarios(session: Session, cwd: Path) -> None:
    if not _require_analysis(session):
        return

    prompt = _build_prompt(
        "generate_test_scenarios",
        requirement=session.requirement,
        analysis=session.analysis,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.test_scenarios = result
        print("\nTest scenarios saved to session.")
        _pause()


def _generate_test_cases(session: Session, cwd: Path) -> None:
    if not _require_scenarios(session):
        return

    prompt = _build_prompt(
        "generate_test_cases",
        requirement=session.requirement,
        analysis=session.analysis,
        scenarios=session.test_scenarios,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.test_cases = result
        print("\nTest cases saved to session.")
        _pause()


def _generate_negative_tests(session: Session, cwd: Path) -> None:
    if not _require_analysis(session):
        return

    prompt = _build_prompt(
        "generate_negative_tests",
        requirement=session.requirement,
        analysis=session.analysis,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.negative_tests = result
        print("\nNegative tests saved to session.")
        _pause()


def _generate_security_tests(session: Session, cwd: Path) -> None:
    if not _require_analysis(session):
        return

    prompt = _build_prompt(
        "generate_security_tests",
        requirement=session.requirement,
        analysis=session.analysis,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.security_tests = result
        print("\nSecurity tests saved to session.")
        _pause()


def _validate_coverage_traceability(session: Session, cwd: Path) -> None:
    if not _require_test_cases(session):
        return

    prompt = _build_prompt(
        "validate_coverage_traceability",
        requirement=session.requirement,
        analysis=session.analysis,
        scenarios=session.test_scenarios,
        test_cases=session.test_cases,
        negative_tests=session.negative_tests,
        security_tests=session.security_tests,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is not None:
        session.coverage_traceability = result
        print("\nCoverage/traceability validation saved to session.")
        _pause()


def _remediate_coverage_gaps(session: Session, cwd: Path) -> None:
    if not _require_coverage_validation(session):
        return

    prompt = _build_prompt(
        "remediate_coverage_gaps",
        requirement=session.requirement,
        analysis=session.analysis,
        scenarios=session.test_scenarios,
        test_cases=session.test_cases,
        coverage_gaps=session.coverage_traceability,
        negative_tests=session.negative_tests,
        security_tests=session.security_tests,
    )
    if prompt is None:
        return

    result = _run_action(cwd, prompt)
    if result is None:
        return

    scenarios_added, cases_added = session.apply_remediation(result)
    if scenarios_added or cases_added:
        parts = []
        if scenarios_added:
            parts.append("scenarios")
        if cases_added:
            parts.append("test cases")
        print(f"\nRemediation appended to session: {', '.join(parts)}.")
        print("Re-run option 6 (Coverage/Traceability Validator) to verify gaps are closed.")
    else:
        print("\nNo new scenarios or test cases were parsed from the response.")
        print("Check Remediation summary in the LLM output or re-run remediation.")
    _pause()


def _export_report(session: Session, output_dir: Path) -> None:
    if not session.has_content():
        print("Nothing to export yet. Run at least one menu action first.")
        _pause()
        return

    result = session.export(output_dir)
    print(f"\nReport exported to: {result.export_dir}")
    print(f"Combined report: {result.combined_report.name}")
    if result.artifact_files:
        print("\nArtifact files:")
        for path in sorted(result.artifact_files, key=lambda p: p.name):
            print(f"  - {path.name}")
    _pause()


def _print_menu() -> None:
    print("\n=== AI Test Planning Agent ===")
    for index, label in enumerate(MENU_OPTIONS, start=1):
        print(f"{index}. {label}")


def run_menu(cwd: Path, output_dir: Path) -> None:
    session = Session()
    handlers = {
        1: lambda: _analyze_requirement(session, cwd),
        2: lambda: _generate_test_scenarios(session, cwd),
        3: lambda: _generate_test_cases(session, cwd),
        4: lambda: _generate_negative_tests(session, cwd),
        5: lambda: _generate_security_tests(session, cwd),
        6: lambda: _validate_coverage_traceability(session, cwd),
        7: lambda: _remediate_coverage_gaps(session, cwd),
        8: lambda: _export_report(session, output_dir),
        9: None,
    }

    while True:
        _print_menu()
        choice = input("\nSelect an option: ").strip()

        if not choice.isdigit():
            print("Enter a number from 1 to 9.")
            _pause()
            continue

        option = int(choice)
        if option == 9:
            print("Goodbye.")
            return

        handler = handlers.get(option)
        if handler is None:
            print("Invalid option. Choose 1-9.")
            _pause()
            continue

        handler()
