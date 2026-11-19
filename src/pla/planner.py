"""Deterministic adaptation planner implementing the rules in ARCHITECTURE.md.

Rule priority:
1. A student override (rejected format) is always respected.
2. Prerequisite gap -> teach the prerequisite, then a fresh check
   (not in the FIXED condition).
3. Self-reported barrier -> matching strategy
   (KNOWLEDGE_AND_BARRIER condition only).
4. Otherwise -> the approved standard activity.
"""

from __future__ import annotations

from .contracts import ALTERNATIVE_ORDER, Barrier, BarrierValue, Condition, Plan, Strategy
from .curriculum import Curriculum
from .learner_model import has_prerequisite_gap, topic_state

BARRIER_TO_STRATEGY = {
    BarrierValue.PACE: Strategy.SMALLER_STEPS,
    BarrierValue.RELEVANCE: Strategy.RELEVANT_EXAMPLE,
    BarrierValue.CONFIDENCE: Strategy.HINTS_LOW_PRESSURE,
}


def plan_next(
    curriculum: Curriculum,
    evidence,
    condition: Condition,
    barrier: Barrier | None = None,
    rejected: frozenset[Strategy] = frozenset(),
    seen_items: set[str] | None = None,
) -> Plan:
    seen = set(seen_items or ()) | {e.item_id for e in evidence}
    target = curriculum.target_topic

    def make(strategy: Strategy, topic: str, reason: str) -> Plan:
        item = curriculum.fresh_item(topic, seen)
        return Plan(strategy, topic, reason, item.id if item else None)

    # 1. Student override.
    if rejected:
        for alt in ALTERNATIVE_ORDER:
            if alt not in rejected:
                return make(alt, target, f"Student rejected {sorted(s.value for s in rejected)}; offering {alt.value} instead.")
        return make(Strategy.STANDARD, target, "All formats rejected; returning to the standard activity.")

    if condition is Condition.FIXED:
        return make(Strategy.STANDARD, target, "Fixed condition: same activity for every student.")

    # 2. Prerequisite gap (observed evidence).
    for prereq in curriculum.prerequisites(target):
        state = topic_state(prereq, evidence)
        if has_prerequisite_gap(state):
            return make(
                Strategy.TEACH_PREREQUISITE,
                prereq,
                f"Most recent answer on prerequisite '{prereq}' ({state.provenance[-1]}) was incorrect; "
                "teach it and check with a new item (tentative, not a label).",
            )

    # 3. Self-reported barrier.
    if condition is Condition.KNOWLEDGE_AND_BARRIER and barrier is not None:
        strategy = BARRIER_TO_STRATEGY[barrier.value]
        return make(strategy, target, f"Student selected barrier '{barrier.value.value}'; using {strategy.value}.")

    # 4. Default.
    reason = "No barrier reported; continuing from educational evidence alone." if barrier is None else (
        "Knowledge-only condition: barrier not used for adaptation."
    )
    return make(Strategy.STANDARD, target, reason)
