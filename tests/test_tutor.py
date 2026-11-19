import io
import json
import urllib.error
from pathlib import Path

import pytest

from pla.contracts import Strategy
from pla.llm import AnthropicAdapter, ModelError, make_adapter
from pla.session import run_session
from pla.tutor import GroundedTutor, build_user_prompt, validate

SCENARIOS = Path(__file__).resolve().parents[1] / "examples" / "scenarios"
APPROVED = ["Equivalent fractions: 1/2 = 2/4 because both numbers were multiplied by 2."]


class FakeAdapter:
    model_id = "fake-model"

    def __init__(self, reply="Here is the idea, slowly:\n1/2 is the same amount as 2/4."):
        self.reply = reply
        self.calls = []

    def generate(self, system, user):
        self.calls.append((system, user))
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply


def load(name):
    return json.loads((SCENARIOS / f"{name}.json").read_text())


# --- validation -------------------------------------------------------------

def test_valid_rewording_is_accepted():
    assert validate("Think of 1/2 as 2/4.", APPROVED) is None


def test_invented_fraction_is_rejected():
    assert validate("1/2 = 3/6 too.", APPROVED).startswith("unapproved_fractions")


def test_empty_and_overlong_outputs_are_rejected():
    assert validate("  ", APPROVED) == "empty_output"
    assert validate("x" * 5000, APPROVED) == "too_long"


# --- tutor ------------------------------------------------------------------

def test_tutor_uses_model_text_when_valid():
    out = GroundedTutor(FakeAdapter(), system_prompt="sys").render(Strategy.SMALLER_STEPS, "Equivalent fractions", APPROVED)
    assert out.used_model and out.fallback_reason is None
    assert out.steps == ["Here is the idea, slowly:", "1/2 is the same amount as 2/4."]


@pytest.mark.parametrize("reply,reason", [
    (ModelError("timeout"), "model_error:ModelError"),
    (RuntimeError("bug"), "unexpected_error:RuntimeError"),
    ("Also 5/10 works!", "unapproved_fractions"),
])
def test_tutor_falls_back_to_approved_text(reply, reason):
    out = GroundedTutor(FakeAdapter(reply), system_prompt="sys").render(Strategy.STANDARD, "T", APPROVED)
    assert not out.used_model
    assert out.steps == APPROVED
    assert out.fallback_reason.startswith(reason)


def test_prompt_contains_strategy_and_approved_content_only():
    prompt = build_user_prompt(Strategy.SMALLER_STEPS, "Equivalent fractions", APPROVED)
    assert "smaller_steps" in prompt
    assert "<approved_content>" in prompt and APPROVED[0] in prompt


def test_default_system_prompt_is_repo_tutor_prompt():
    assert "educational tutor" in GroundedTutor(FakeAdapter()).system_prompt


# --- session integration ----------------------------------------------------

def test_planner_decisions_are_unchanged_by_the_model():
    for name in ["pace", "relevance", "prerequisite_gap", "override"]:
        plain = run_session(load(name)).strategies
        with_model = run_session(load(name), tutor=GroundedTutor(FakeAdapter(), "sys")).strategies
        assert plain == with_model


def test_record_logs_model_version_and_fallbacks():
    tutor = GroundedTutor(FakeAdapter(ModelError("down")), "sys")
    record = run_session(load("pace"), tutor=tutor).record.to_dict()
    assert record["model_id"] == "fake-model"
    assert record["prompt_version"] == tutor.prompt_version
    lesson = next(e for e in record["events"] if e["type"] == "lesson_offered")
    assert lesson["wording"] == "approved_text_fallback"


def test_student_free_text_is_never_sent_to_model():
    fake = FakeAdapter()
    scenario = load("relevance")
    run_session(scenario, tutor=GroundedTutor(fake, "sys"))
    sent = " ".join(user for _, user in fake.calls)
    assert scenario["check_in"]["goal"] not in sent
    for answer in scenario["answers"].values():
        assert f"A: {answer}" not in sent


# --- Anthropic adapter (no network) ----------------------------------------

def test_adapter_requires_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ModelError):
        AnthropicAdapter()


def test_adapter_parses_text(monkeypatch):
    a = AnthropicAdapter(api_key="test")
    monkeypatch.setattr(a, "_request", lambda p: {"content": [{"type": "text", "text": " hi "}]})
    assert a.generate("s", "u") == "hi"


def http_error(code):
    return urllib.error.HTTPError("u", code, "err", {}, io.BytesIO(b""))


def test_adapter_retries_transient_errors_then_succeeds(monkeypatch):
    a = AnthropicAdapter(api_key="test", max_retries=2)
    calls = []

    def fake(payload):
        calls.append(1)
        if len(calls) < 2:
            raise http_error(503)
        return {"content": [{"type": "text", "text": "ok"}]}

    monkeypatch.setattr(a, "_request", fake)
    monkeypatch.setattr("pla.llm.time.sleep", lambda s: None)
    assert a.generate("s", "u") == "ok" and len(calls) == 2


def test_adapter_does_not_retry_client_errors(monkeypatch):
    a = AnthropicAdapter(api_key="test", max_retries=2)
    calls = []

    def fake(payload):
        calls.append(1)
        raise http_error(400)

    monkeypatch.setattr(a, "_request", fake)
    with pytest.raises(ModelError):
        a.generate("s", "u")
    assert len(calls) == 1


def test_make_adapter_none_means_deterministic():
    assert make_adapter("none") is None and make_adapter(None) is None
