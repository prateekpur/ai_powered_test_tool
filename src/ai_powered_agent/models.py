from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class RequirementPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Requirement:
    title: str
    description: str
    id: str = field(default_factory=lambda: str(uuid4()))
    priority: RequirementPriority = RequirementPriority.MEDIUM
    source: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_markdown(self) -> str:
        lines = [
            f"**ID:** {self.id}",
            f"**Title:** {self.title}",
            f"**Priority:** {self.priority.value}",
        ]
        if self.source:
            lines.append(f"**Source:** {self.source}")
        lines.extend(["", self.description.strip()])
        if self.acceptance_criteria:
            lines.extend(["", "**Acceptance criteria:**"])
            lines.extend(f"- {item}" for item in self.acceptance_criteria)
        return "\n".join(lines)


@dataclass
class RequirementAnalysis:
    requirement_id: str
    raw_response: str = ""
    summary: str = ""
    functional_requirements: list[str] = field(default_factory=list)
    non_functional_requirements: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)

    def has_content(self) -> bool:
        return bool(
            self.raw_response.strip()
            or self.summary.strip()
            or any(
                (
                    self.functional_requirements,
                    self.non_functional_requirements,
                    self.assumptions,
                    self.risks,
                    self.open_questions,
                )
            )
        )

    def to_markdown(self) -> str:
        if self.raw_response.strip():
            return self.raw_response.strip()

        sections: list[tuple[str, list[str] | str]] = [
            ("Summary", self.summary),
            ("Functional requirements", self.functional_requirements),
            ("Non-functional requirements", self.non_functional_requirements),
            ("Assumptions", self.assumptions),
            ("Risks", self.risks),
            ("Open questions", self.open_questions),
        ]
        lines: list[str] = []
        for title, content in sections:
            if isinstance(content, str):
                if not content.strip():
                    continue
                lines.extend([f"### {title}", "", content.strip(), ""])
                continue
            if not content:
                continue
            lines.extend([f"### {title}", ""])
            lines.extend(f"- {item}" for item in content)
            lines.append("")
        return "\n".join(lines).strip()
