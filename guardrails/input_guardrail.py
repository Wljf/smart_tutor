from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class GuardrailDecision:
    allowed: bool
    reason: str
    response: str


class NeMoGuardrailsLayer:
    """Loads a NeMo-style guardrails configuration file."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.raw_config = self._load_config(config_path)
        self.policies = self.raw_config.get("policies", {})

    @staticmethod
    def _load_config(config_path: Path) -> dict[str, Any]:
        with config_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}


class InputGuardrail:
    """Rejects clearly unsafe or obviously unrelated requests before routing."""

    def __init__(self, guardrails_layer: NeMoGuardrailsLayer) -> None:
        self.guardrails_layer = guardrails_layer
        self.reject_message = guardrails_layer.policies.get(
            "reject_message",
            "Sorry, I can only help with math or history homework questions.",
        )
        self.unsafe_patterns = self._normalize_patterns(
            guardrails_layer.policies.get("unsafe_patterns", [])
        )
        self.unrelated_patterns = self._normalize_patterns(
            guardrails_layer.policies.get("clearly_unrelated_patterns", [])
        )

    def validate(self, query: str) -> GuardrailDecision:
        normalized_query = query.strip().lower()

        if not normalized_query:
            return GuardrailDecision(
                allowed=False,
                reason="empty_query",
                response="Please ask a math or history homework question.",
            )

        if self._matches_any(normalized_query, self.unsafe_patterns):
            return GuardrailDecision(
                allowed=False,
                reason="unsafe_query",
                response="I cannot help with unsafe requests.",
            )

        if self._matches_any(normalized_query, self.unrelated_patterns):
            return GuardrailDecision(
                allowed=False,
                reason="clearly_unrelated_query",
                response=self.reject_message,
            )

        return GuardrailDecision(
            allowed=True,
            reason="allowed",
            response="",
        )

    @staticmethod
    def _normalize_patterns(patterns: list[str]) -> list[str]:
        return [pattern.strip().lower() for pattern in patterns if pattern.strip()]

    @staticmethod
    def _matches_any(text: str, patterns: list[str]) -> bool:
        return any(pattern in text for pattern in patterns)
