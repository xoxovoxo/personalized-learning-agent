"""Typed versions of the session contract described in ARCHITECTURE.md.

Self-report, observed performance and planner hypotheses are kept in
separate fields so they can never be confused with each other.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Literal

SCHEMA_VERSION = "0.1"


class Condition(str, Enum):
    """Comparison conditions from EVALUATION.md (X01)."""

    FIXED = "fixed"
    KNOWLEDGE_ONLY = "knowledge_only"
    KNOWLEDGE_AND_BARRIER = "knowledge_and_barrier"


class BarrierValue(str, Enum):
    PACE = "pace"
    RELEVANCE = "relevance"
    CONFIDENCE = "confidence"


class Strategy(str, Enum):
    STANDARD = "standard"
    TEACH_PREREQUISITE = "teach_prerequisite"
    SMALLER_STEPS = "smaller_steps"
    RELEVANT_EXAMPLE = "relevant_example"
    HINTS_LOW_PRESSURE = "hints_low_pressure"


# Order in which alternatives are offered after a student rejects a format.
ALTERNATIVE_ORDER = [
    Strategy.SMALLER_STEPS,
    Strategy.RELEVANT_EXAMPLE,
    Strategy.HINTS_LOW_PRESSURE,
    Strategy.STANDARD,
]


@dataclass(frozen=True)
class Evidence:
    """One observed answer. This is observed performance, not inference."""

    item_id: str
    topic_id: str
    correct: bool


@dataclass(frozen=True)
class Barrier:
    """A barrier the student chose to report. Always self-reported."""

    value: BarrierValue
    source: Literal["student_selected"] = "student_selected"


@dataclass(frozen=True)
class TopicState:
    """Tentative, session-only summary of evidence for one topic.

    `status` is a hypothesis with explicit uncertainty and provenance;
    it is never a permanent ability label.
    """

    topic_id: str
    attempts: int
    correct: int
    status: Literal["insufficient_evidence", "developing", "secure"]
    uncertainty: Literal["high", "moderate", "low"]
    provenance: tuple[str, ...]
    latest_correct: bool | None


@dataclass(frozen=True)
class Plan:
    strategy: Strategy
    topic_id: str
    reason: str
    next_item_id: str | None
    student_can_override: bool = True


@dataclass
class SessionRecord:
    """Minimal research record. Free text is excluded by default."""

    session_id: str
    topic_id: str
    condition: Condition
    curriculum_version: str
    fictional: bool = True
    schema_version: str = SCHEMA_VERSION
    prompt_version: str = "none-deterministic"
    model_id: str | None = None
    evidence: list[Evidence] = field(default_factory=list)
    barrier: Barrier | None = None
    events: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        def convert(value):
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [convert(v) for v in value]
            return value

        return convert(asdict(self))
