import json
from pathlib import Path

import pytest

from pla.contracts import Strategy
from pla.curriculum import Curriculum
from pla.session import run_session

SCENARIOS = Path(__file__).resolve().parents[1] / "examples" / "scenarios"


def load(name):
    return json.loads((SCENARIOS / f"{name}.json").read_text())


def test_pace_scenario_uses_smaller_steps():
    result = run_session(load("pace"))
    assert result.strategies == [Strategy.SMALLER_STEPS]


def test_relevance_scenario_uses_student_interest():
    result = run_session(load("relevance"))
    assert result.strategies == [Strategy.RELEVANT_EXAMPLE]
    assert any("recipe" in line for line in result.transcript)


def test_prerequisite_gap_scenario_teaches_prerequisite_first():
    result = run_session(load("prerequisite_gap"))
    assert result.strategies == [Strategy.TEACH_PREREQUISITE, Strategy.STANDARD]


def test_override_scenario_switches_format():
    result = run_session(load("override"))
    assert result.strategies[0] is Strategy.SMALLER_STEPS
    assert result.strategies[1] is not Strategy.SMALLER_STEPS


def test_fixed_condition_gives_everyone_the_standard_lesson():
    for name in ["pace", "relevance", "prerequisite_gap"]:
        scenario = load(name) | {"condition": "fixed"}
        assert set(run_session(scenario).strategies) == {Strategy.STANDARD}


def test_unclear_answer_records_no_evidence():
    result = run_session(load("pace"))
    assert "baseline-03" not in [e.item_id for e in result.record.evidence]
    assert {"type": "answer_unclear", "item_id": "baseline-03"} in result.record.events


def test_research_record_contains_no_free_text():
    scenario = load("relevance")
    record = json.dumps(run_session(scenario).record.to_dict())
    assert scenario["check_in"]["goal"] not in record
    assert "cooking" not in record
    assert "recipe" not in record


def test_non_fictional_scenarios_are_refused():
    with pytest.raises(ValueError):
        run_session(load("pace") | {"fictional": False})


def test_every_lesson_and_item_is_reachable():
    cur = Curriculum.load()
    for topic, lessons in cur.lessons.items():
        assert topic in cur.topics
        for lesson in lessons.values():
            assert lesson["source_id"] and lesson["steps"]
    for item in cur.items.values():
        assert item.topic in cur.topics and item.accepted
