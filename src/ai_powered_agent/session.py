import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ai_powered_agent.models import Requirement, RequirementAnalysis


@dataclass
class ExportResult:
    export_dir: Path
    combined_report: Path
    artifact_files: list[Path]


@dataclass
class Session:
    requirement: Requirement | None = None
    analysis: RequirementAnalysis | None = None
    test_scenarios: str = ""
    test_cases: str = ""
    negative_tests: str = ""
    security_tests: str = ""
    coverage_traceability: str = ""
    schema_validation: str = ""
    remediation_log: str = ""

    def append_scenarios(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        separator = "\n\n---\n\n## Remediation additions (scenarios)\n\n"
        if self.test_scenarios.strip():
            self.test_scenarios = self.test_scenarios.rstrip() + separator + text
        else:
            self.test_scenarios = text

    def append_test_cases(self, text: str, *, section: str = "Remediation additions (test cases)") -> None:
        text = text.strip()
        if not text:
            return
        separator = f"\n\n---\n\n## {section}\n\n"
        if self.test_cases.strip():
            self.test_cases = self.test_cases.rstrip() + separator + text
        else:
            self.test_cases = text

    @staticmethod
    def _extract_markdown_section(text: str, section_title: str) -> str:
        pattern = rf"^## {re.escape(section_title)}\s*$"
        match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
        if not match:
            return ""
        start = match.end()
        next_section = re.search(r"^## ", text[start:], flags=re.MULTILINE)
        end = start + next_section.start() if next_section else len(text)
        return text[start:end].strip()

    def apply_remediation(self, response: str) -> tuple[bool, bool]:
        """Parse remediation LLM output and append new scenarios/test cases."""
        new_scenarios = self._extract_markdown_section(response, "New Scenarios")
        new_test_cases = self._extract_markdown_section(response, "New Test Cases")
        clarifications = self._extract_markdown_section(response, "Requirement clarifications needed")
        summary = self._extract_markdown_section(response, "Remediation summary")

        if new_scenarios:
            self.append_scenarios(new_scenarios)
        if new_test_cases:
            self.append_test_cases(new_test_cases)

        log_parts: list[str] = []
        if summary:
            log_parts.append(f"## Remediation summary\n\n{summary}")
        if clarifications:
            log_parts.append(f"## Requirement clarifications needed\n\n{clarifications}")
        if log_parts:
            entry = "\n\n".join(log_parts)
            if self.remediation_log.strip():
                self.remediation_log = self.remediation_log.rstrip() + "\n\n---\n\n" + entry
            else:
                self.remediation_log = entry

        return bool(new_scenarios), bool(new_test_cases)

    def has_content(self) -> bool:
        return any(
            (
                self.requirement is not None,
                self.analysis is not None and self.analysis.has_content(),
                self.test_scenarios.strip(),
                self.test_cases.strip(),
                self.negative_tests.strip(),
                self.security_tests.strip(),
                self.coverage_traceability.strip(),
                self.schema_validation.strip(),
                self.remediation_log.strip(),
            )
        )

    def _artifact_sections(self) -> list[tuple[str, str, str]]:
        """Return (filename_stem, report_heading, body) for each populated artifact."""
        sections: list[tuple[str, str, str]] = []

        if self.requirement is not None:
            sections.append(
                ("requirement", "Requirement", self.requirement.to_markdown())
            )
        if self.analysis is not None and self.analysis.has_content():
            sections.append(
                ("analysis", "Requirement Analysis", self.analysis.to_markdown())
            )
        if self.test_scenarios.strip():
            sections.append(
                ("test_scenarios", "Test Scenarios", self.test_scenarios.strip())
            )
        if self.test_cases.strip():
            sections.append(("test_cases", "Test Cases", self.test_cases.strip()))
        if self.negative_tests.strip():
            sections.append(
                ("negative_tests", "Negative Tests", self.negative_tests.strip())
            )
        if self.security_tests.strip():
            sections.append(
                ("security_tests", "Security Tests", self.security_tests.strip())
            )
        if self.coverage_traceability.strip():
            sections.append(
                (
                    "coverage_traceability",
                    "Coverage/Traceability Validation",
                    self.coverage_traceability.strip(),
                )
            )
        if self.schema_validation.strip():
            sections.append(
                ("schema_validation", "Schema Validation", self.schema_validation.strip())
            )
        if self.remediation_log.strip():
            sections.append(
                ("remediation_log", "Remediation Log", self.remediation_log.strip())
            )
        return sections

    def _report_header(self, exported_at: datetime) -> str:
        lines = [
            "# Test Planning Report",
            "",
            f"- **Exported:** {exported_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        ]
        if self.requirement is not None:
            lines.append(f"- **Requirement:** {self.requirement.title}")
            lines.append(f"- **Requirement ID:** {self.requirement.id}")
            if self.requirement.source:
                lines.append(f"- **Source:** {self.requirement.source}")
        lines.append("")
        return "\n".join(lines)

    def to_markdown(self, *, exported_at: datetime | None = None) -> str:
        exported_at = exported_at or datetime.now(timezone.utc)
        lines = [self._report_header(exported_at)]

        artifact_files = [f"{stem}.md" for stem, _, _ in self._artifact_sections()]
        if artifact_files:
            lines.extend(["## Artifacts", ""])
            lines.extend(f"- `{name}`" for name in artifact_files)
            lines.append("")

        for _, heading, body in self._artifact_sections():
            lines.extend([f"## {heading}", "", body, ""])

        return "\n".join(lines).rstrip() + "\n"

    def _write_manifest(self, export_dir: Path, artifact_files: list[str], exported_at: datetime) -> Path:
        manifest = {
            "exported_at": exported_at.isoformat(),
            "requirement": None,
            "artifacts": artifact_files,
        }
        if self.requirement is not None:
            manifest["requirement"] = {
                "id": self.requirement.id,
                "title": self.requirement.title,
                "source": self.requirement.source,
                "priority": self.requirement.priority.value,
            }
        path = export_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def export(self, output_dir: Path) -> ExportResult:
        """Export all session artifacts to a timestamped folder under output_dir."""
        exported_at = datetime.now(timezone.utc)
        timestamp = exported_at.strftime("%Y%m%d_%H%M%S")
        export_dir = output_dir / f"test_plan_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)

        artifact_paths: list[Path] = []
        artifact_names: list[str] = []

        for stem, _, body in self._artifact_sections():
            path = export_dir / f"{stem}.md"
            path.write_text(body + "\n", encoding="utf-8")
            artifact_paths.append(path)
            artifact_names.append(path.name)

        combined_report = export_dir / "test_report.md"
        combined_report.write_text(
            self.to_markdown(exported_at=exported_at),
            encoding="utf-8",
        )

        manifest_path = self._write_manifest(export_dir, artifact_names, exported_at)

        return ExportResult(
            export_dir=export_dir,
            combined_report=combined_report,
            artifact_files=artifact_paths + [manifest_path],
        )
