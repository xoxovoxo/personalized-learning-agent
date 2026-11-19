"""Local session runner for scripted, fictional students.

Run a scenario:
    python -m pla.session examples/scenarios/pace.json

The transcript (lesson text and prompts) is for humans. The research
record holds item IDs, correctness, strategies and reasons only - no free text.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

from .contracts import Barrier, BarrierValue, Condition, Evidence, SessionRecord, Strategy
from .curriculum import Curriculum
from .learner_model import topic_state
from .llm import ModelError, make_adapter
from .planner import plan_next
from .tutor import GroundedTutor


@dataclass
class SessionResult:
    record: SessionRecord
    transcript: list[str] = field(default_factory=list)
    strategies: list[Strategy] = field(default_factory=list)


def render_lesson(curriculum: Curriculum, topic: str, strategy: Strategy, interest: str | None) -> tuple[str, list[str]]:
    lesson = curriculum.lessons[topic][strategy.value]
    steps = list(lesson["steps"])
    if strategy is Strategy.RELEVANT_EXAMPLE:
        example = lesson["interest_templates"].get(interest or "", lesson["fallback"])
        steps = [s.replace("{example}", example) for s in steps]
    return lesson["source_id"], steps


def run_session(scenario: dict, curriculum: Curriculum | None = None, tutor: GroundedTutor | None = None) -> SessionResult:
    if not scenario.get("fictional", False):
        raise ValueError("Only fictional scenarios may be run in this demonstrator.")
    curriculum = curriculum or Curriculum.load()

    check_in = scenario.get("check_in", {})
    barrier_value = check_in.get("barrier")
    barrier = Barrier(BarrierValue(barrier_value)) if barrier_value else None
    interest = check_in.get("interest")
    answers: dict = scenario.get("answers", {})
    feedback: list = list(scenario.get("feedback", []))
    max_cycles = scenario.get("max_cycles", 4)

    record = SessionRecord(
        session_id=scenario["session_id"],
        topic_id=curriculum.target_topic,
        condition=Condition(scenario["condition"]),
        curriculum_version=curriculum.version,
        barrier=barrier,
    )
    if tutor is not None:
        record.prompt_version = tutor.prompt_version
        record.model_id = tutor.adapter.model_id
    result = SessionResult(record)
    say = result.transcript.append
    seen: set[str] = set()

    def ask(item_id: str) -> bool | None:
        item = curriculum.items[item_id]
        seen.add(item_id)
        say(f"  Q [{item_id}] {item.prompt}")
        answer = answers.get(item_id)
        correct = curriculum.check(item_id, answer)
        if correct is None:
            say("  Student skipped or gave an unclear answer -> no evidence recorded; will ask for clarification.")
            record.events.append({"type": "answer_unclear", "item_id": item_id})
            return None
        say(f"  A: {answer} -> {'correct' if correct else 'not yet'}")
        record.evidence.append(Evidence(item_id, item.topic, correct))
        record.events.append({"type": "answer", "item_id": item_id, "correct": correct})
        return correct

    # Check-in: everything optional.
    say("CHECK-IN (all questions optional)")
    say(f"  Barrier: {barrier.value.value if barrier else 'skipped'}; interest: {interest or 'skipped'}")
    record.events.append({
        "type": "check_in",
        "barrier_selected": barrier.value.value if barrier else None,
        "interest_provided": interest is not None,
    })

    say("BASELINE")
    for item in curriculum.baseline_items():
        ask(item.id)

    rejected: set[Strategy] = set()
    for cycle in range(1, max_cycles + 1):
        plan = plan_next(curriculum, record.evidence, record.condition, barrier, frozenset(rejected), seen)
        source_id, steps = render_lesson(curriculum, plan.topic_id, plan.strategy, interest)
        wording = {"wording": "approved_text"}
        if tutor is not None:
            out = tutor.render(plan.strategy, curriculum.topics[plan.topic_id]["title"], steps)
            steps = out.steps
            wording = {"wording": "model" if out.used_model else "approved_text_fallback",
                       "fallback_reason": out.fallback_reason}
            if out.fallback_reason:
                say(f"  (model output not used: {out.fallback_reason}; showing approved text)")
        result.strategies.append(plan.strategy)
        say(f"CYCLE {cycle}: {plan.strategy.value} on {plan.topic_id}")
        say(f"  Why: {plan.reason}")
        for step in steps:
            say(f"  > {step}")
        record.events.append({
            "type": "lesson_offered",
            "cycle": cycle,
            "strategy": plan.strategy.value,
            "topic_id": plan.topic_id,
            "reason": plan.reason,
            "source_id": source_id,
            **wording,
        })

        correct = ask(plan.next_item_id) if plan.next_item_id else None

        response = feedback.pop(0) if feedback else "helped"
        say(f"  Did this approach help? -> {response}")
        record.events.append({"type": "feedback", "cycle": cycle, "response": response})
        if response == "reject":
            rejected.add(plan.strategy)
            continue

        target = topic_state(curriculum.target_topic, record.evidence)
        if plan.topic_id == curriculum.target_topic and correct and target.latest_correct:
            say(f"END: target check correct. Topic state: {target.status} "
                f"(uncertainty {target.uncertainty}, evidence {list(target.provenance)}).")
            say("  Next step: one more equivalent-fractions problem without hints.")
            break
        if plan.next_item_id is None:
            say("END: no unseen practice items left for this topic.")
            break
    else:
        say("END: cycle limit reached; recommend teacher review.")

    record.events.append({"type": "session_end"})
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--condition", choices=[c.value for c in Condition], help="override the scenario's condition")
    parser.add_argument("--record", action="store_true", help="also print the research record as JSON")
    parser.add_argument("--model", choices=["none", "anthropic"], default="none",
                        help="reword approved lessons with a model (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--model-id", help="override the model identifier")
    args = parser.parse_args(argv)

    scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
    if args.condition:
        scenario["condition"] = args.condition
    try:
        adapter = make_adapter(args.model, args.model_id)
    except ModelError as e:
        parser.exit(2, f"error: {e} Set it in your shell, or run without --model.\n")
    result = run_session(scenario, tutor=GroundedTutor(adapter) if adapter else None)
    print("\n".join(result.transcript))
    if args.record:
        print(json.dumps(result.record.to_dict(), indent=2))


if __name__ == "__main__":
    main()
