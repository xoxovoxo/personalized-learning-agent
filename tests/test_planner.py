import pytest

from pla.contracts import Barrier, BarrierValue, Condition, Evidence, Strategy
from pla.curriculum import Curriculum
from pla.learner_model import topic_state
from pla.planner import plan_next


@pytest.fixture(scope="module")
def cur():
    return Curriculum.load()


def ev(item, topic, ok):
    return Evidence(item, topic, ok)


PREREQ_WRONG = [ev("baseline-02", "fractions-meaning", False)]
PREREQ_RIGHT = [ev("baseline-02", "fractions-meaning", True)]


def test_prerequisite_gap_teaches_prerequisite_with_fresh_item(cur):
    plan = plan_next(cur, PREREQ_WRONG, Condition.KNOWLEDGE_AND_BARRIER)
    assert plan.strategy is Strategy.TEACH_PREREQUISITE
    assert plan.topic_id == "fractions-meaning"
    assert plan.next_item_id == "meaning-01"


def test_prerequisite_gap_clears_after_correct_fresh_check(cur):
    evidence = PREREQ_WRONG + [ev("meaning-01", "fractions-meaning", True)]
    plan = plan_next(cur, evidence, Condition.KNOWLEDGE_ONLY)
    assert plan.strategy is Strategy.STANDARD


@pytest.mark.parametrize("barrier,expected", [
    (BarrierValue.PACE, Strategy.SMALLER_STEPS),
    (BarrierValue.RELEVANCE, Strategy.RELEVANT_EXAMPLE),
    (BarrierValue.CONFIDENCE, Strategy.HINTS_LOW_PRESSURE),
])
def test_barrier_maps_to_strategy(cur, barrier, expected):
    plan = plan_next(cur, PREREQ_RIGHT, Condition.KNOWLEDGE_AND_BARRIER, Barrier(barrier))
    assert plan.strategy is expected


def test_skipped_barrier_uses_evidence_alone(cur):
    plan = plan_next(cur, PREREQ_RIGHT, Condition.KNOWLEDGE_AND_BARRIER, None)
    assert plan.strategy is Strategy.STANDARD


def test_knowledge_only_ignores_barrier(cur):
    plan = plan_next(cur, PREREQ_RIGHT, Condition.KNOWLEDGE_ONLY, Barrier(BarrierValue.PACE))
    assert plan.strategy is Strategy.STANDARD


def test_fixed_condition_ignores_gap_and_barrier(cur):
    plan = plan_next(cur, PREREQ_WRONG, Condition.FIXED, Barrier(BarrierValue.PACE))
    assert plan.strategy is Strategy.STANDARD


def test_override_is_respected(cur):
    plan = plan_next(cur, PREREQ_RIGHT, Condition.KNOWLEDGE_AND_BARRIER,
                     Barrier(BarrierValue.PACE), rejected=frozenset({Strategy.SMALLER_STEPS}))
    assert plan.strategy is not Strategy.SMALLER_STEPS
    assert plan.student_can_override


def test_check_item_is_never_a_repeat(cur):
    seen = {"equiv-01", "equiv-02"}
    plan = plan_next(cur, PREREQ_RIGHT, Condition.KNOWLEDGE_ONLY, seen_items=seen)
    assert plan.next_item_id not in seen


def test_single_answer_is_insufficient_evidence():
    state = topic_state("fractions-meaning", PREREQ_WRONG)
    assert state.status == "insufficient_evidence"
    assert state.uncertainty == "high"
    assert state.provenance == ("baseline-02",)
