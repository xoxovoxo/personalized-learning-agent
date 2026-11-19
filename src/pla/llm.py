"""Provider-independent model adapter (backlog S04).

The rest of the code depends only on the `ModelAdapter` protocol, so the
provider can be swapped without touching the planner or tutor. Credentials
are read from the server environment and never stored in the repository.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class ModelError(Exception):
    """Any failure to obtain usable text from a model."""


class ModelAdapter(Protocol):
    model_id: str

    def generate(self, system: str, user: str) -> str:
        """Return the model's text, or raise ModelError."""


@dataclass
class AnthropicAdapter:
    """Calls the Anthropic Messages API with the standard library only.

    - API key from the ANTHROPIC_API_KEY environment variable
    - temperature 0 by default, for more repeatable wording
    - per-request timeout and bounded retries on transient errors
    """

    model_id: str = "claude-sonnet-5-5"
    max_tokens: int = 600
    temperature: float = 0.0
    timeout_s: float = 20.0
    max_retries: int = 2
    api_key: str | None = None
    url: str = "https://api.anthropic.com/v1/messages"

    def __post_init__(self):
        self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ModelError("ANTHROPIC_API_KEY is not set.")

    def _request(self, payload: dict) -> dict:
        req = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read())

    def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                data = self._request(payload)
                text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
                if not text.strip():
                    raise ModelError("Empty model response.")
                return text.strip()
            except urllib.error.HTTPError as e:
                last_error = e
                if e.code not in (429, 500, 502, 503, 529):
                    break  # not transient: do not retry
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
                last_error = e
            if attempt < self.max_retries:
                time.sleep(min(2 ** attempt, 4))
        raise ModelError(f"Model call failed: {last_error}")


def make_adapter(name: str | None, model_id: str | None = None) -> ModelAdapter | None:
    """Factory used by the CLI. `None` or "none" means deterministic text only."""
    if not name or name == "none":
        return None
    if name == "anthropic":
        return AnthropicAdapter(model_id=model_id) if model_id else AnthropicAdapter()
    raise ValueError(f"Unknown model provider: {name}")
