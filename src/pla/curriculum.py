"""Load the approved curriculum and check answers deterministically."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRICULUM = REPO_ROOT / "curriculum" / "fractions-equivalence.json"


@dataclass(frozen=True)
class Item:
    id: str
    topic: str
    role: str
    prompt: str
    accepted: tuple[str, ...]


def normalize(answer: str) -> str:
    return "".join(answer.lower().split()).rstrip(".")


class Curriculum:
    def __init__(self, data: dict):
        self.version: str = data["curriculum_version"]
        self.target_topic: str = data["target_topic"]
        self.topics: dict = data["topics"]
        self.lessons: dict = data["lessons"]
        self.items: dict[str, Item] = {
            raw["id"]: Item(
                id=raw["id"],
                topic=raw["topic"],
                role=raw["role"],
                prompt=raw["prompt"],
                accepted=tuple(normalize(a) for a in raw["accepted"]),
            )
            for raw in data["items"]
        }

    @classmethod
    def load(cls, path: Path | str = DEFAULT_CURRICULUM) -> "Curriculum":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def prerequisites(self, topic_id: str) -> list[str]:
        return list(self.topics[topic_id]["prerequisites"])

    def baseline_items(self) -> list[Item]:
        return [i for i in self.items.values() if i.role == "baseline"]

    def fresh_item(self, topic_id: str, seen: set[str]) -> Item | None:
        """First unseen practice item for a topic (deterministic order)."""
        for item in self.items.values():
            if item.topic == topic_id and item.role == "practice" and item.id not in seen:
                return item
        return None

    def check(self, item_id: str, answer: str | None) -> bool | None:
        """True/False for a clear answer; None when empty (ask to clarify)."""
        if answer is None or not normalize(answer):
            return None
        return normalize(answer) in self.items[item_id].accepted
