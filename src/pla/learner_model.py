"""Session-only learner model: topic evidence with uncertainty and provenance."""

from __future__ import annotations

from .contracts import Evidence, TopicState


def topic_state(topic_id: str, evidence: list[Evidence]) -> TopicState:
    relevant = [e for e in evidence if e.topic_id == topic_id]
    attempts = len(relevant)
    correct = sum(e.correct for e in relevant)

    if attempts < 2:
        status = "insufficient_evidence"
    elif correct / attempts >= 0.8:
        status = "secure"
    else:
        status = "developing"

    uncertainty = "high" if attempts < 2 else "moderate" if attempts < 4 else "low"

    return TopicState(
        topic_id=topic_id,
        attempts=attempts,
        correct=correct,
        status=status,
        uncertainty=uncertainty,
        provenance=tuple(e.item_id for e in relevant),
        latest_correct=relevant[-1].correct if relevant else None,
    )


def has_prerequisite_gap(state: TopicState) -> bool:
    """A gap is a tentative hypothesis: the most recent prerequisite answer was wrong.

    One wrong answer triggers re-teaching plus a fresh check; it does not
    produce a lasting label. A later correct answer clears it.
    """
    return state.latest_correct is False
