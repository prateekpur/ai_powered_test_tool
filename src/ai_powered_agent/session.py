from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ai_powered_agent.models import Requirement, RequirementAnalysis


@dataclass
class Session:
    requirement: Requirement | None = None
    analysis: RequirementAnalysis | None = None
    test_scenarios: str = ""
    test_cases: str = ""
    negative_tests: str = ""
    security_tests: str = ""

    def has_content(self) -> bool:
        return any(
            (
                self.requirement is not None,
                self.analysis is not None and self.analysis.has_content(),
                self.test_scenarios.strip(),
                self.test_cases.strip(),
                self.negative_tests.strip(),
                self.security_tests.strip(),
            )
        )

    def to_markdown(self) -> str:
        sections: list[tuple[str, str]] = []

        if self.requirement is not None:
            sections.append(("Requirement", self.requirement.to_markdown()))
        if self.analysis is not None and self.analysis.has_content():
            sections.append(("Requirement Analysis", self.analysis.to_markdown()))
        if self.test_scenarios.strip():
            sections.append(("Test Scenarios", self.test_scenarios))
        if self.test_cases.strip():
            sections.append(("Test Cases", self.test_cases))
        if self.negative_tests.strip():
            sections.append(("Negative Tests", self.negative_tests))
        if self.security_tests.strip():
            sections.append(("Security Tests", self.security_tests))

        lines = ["# Test Planning Report", ""]
        for title, body in sections:
            lines.extend([f"## {title}", "", body.strip(), ""])
        return "\n".join(lines).rstrip() + "\n"

    def export(self, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = output_dir / f"test_report_{timestamp}.md"
        path.write_text(self.to_markdown(), encoding="utf-8")
        return path
