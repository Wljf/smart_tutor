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
    """Rejects unsafe, unrelated, and low-value local trivia queries."""

    def __init__(self, guardrails_layer: NeMoGuardrailsLayer) -> None:
        self.guardrails_layer = guardrails_layer
        policies = guardrails_layer.policies

        self.reject_message = policies.get(
            "reject_message",
            "Sorry, I can only help with math or history homework questions.",
        )

        self.unsafe_message = policies.get(
            "unsafe_message",
            "I cannot help with unsafe requests.",
        )

        self.local_trivia_message = policies.get(
            "local_trivia_message",
            (
                "Sorry, I focus on meaningful historical topics rather than "
                "niche institutional facts."
            ),
        )

        self.unsafe_patterns = self._normalize_patterns(
            policies.get("unsafe_patterns", [])
        )

        self.unrelated_patterns = self._normalize_patterns(
            policies.get("clearly_unrelated_patterns", [])
        )

        self.local_trivia_patterns = self._normalize_patterns(
            policies.get("local_trivia_patterns", [])
        )

    # -----------------------------
    # 主入口
    # -----------------------------
    def validate(self, query: str) -> GuardrailDecision:
        normalized_query = query.strip().lower()

        if not normalized_query:
            return GuardrailDecision(
                allowed=False,
                reason="empty_query",
                response="Please ask a math or history homework question.",
            )

        if self._is_unsafe_query(normalized_query):
            return GuardrailDecision(
                allowed=False,
                reason="unsafe_query",
                response=self.unsafe_message,
            )

        if self._is_local_trivia_query(normalized_query):
            return GuardrailDecision(
                allowed=False,
                reason="local_trivia_query",
                response=self.local_trivia_message,
            )

        if self._is_non_homework_query(normalized_query):
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

    @classmethod
    def _contains_any(cls, text: str, terms: tuple[str, ...]) -> bool:
        return cls._matches_any(text, list(terms))

    def _is_unsafe_query(self, text: str) -> bool:
        if self._matches_any(text, self.unsafe_patterns):
            return True

        dangerous_objects = (
            "firecracker", "explosive", "bomb", "molotov",
            "poison", "weapon", "gun", "knife",
        )

        dangerous_actions = (
            "throw", "set off", "light", "ignite",
            "detonate", "build", "make", "use",
            "hurt", "kill", "attack", "shoot", "stab",
        )

        risky_contexts = (
            "busy street", "crowd", "school",
            "classroom", "public place", "someone", "people",
        )

        if self._contains_any(text, dangerous_objects) and self._contains_any(text, dangerous_actions):
            return True

        if "what would happen if" in text and self._contains_any(text, dangerous_objects):
            return True

        return self._contains_any(text, dangerous_objects) and self._contains_any(text, risky_contexts)

    def _is_non_homework_query(self, text: str) -> bool:
        if self._matches_any(text, self.unrelated_patterns):
            return True

        planning_verbs = (
            "best way", "recommend", "suggest", "plan",
            "book", "choose", "where should i",
        )

        travel_terms = (
            "travel", "trip", "flight", "airport",
            "hotel", "vacation", "holiday", "restaurant", "tour",
        )

        lifestyle_terms = (
            "movie", "tv show", "celebrity", "shopping",
            "buy", "purchase", "recipe", "dating",
            "relationship", "fashion",
        )

        if self._contains_any(text, planning_verbs) and (
            self._contains_any(text, travel_terms)
            or self._contains_any(text, lifestyle_terms)
        ):
            return True

        return self._contains_any(text, lifestyle_terms) and not self._contains_any(
            text,
            ("history", "historical", "math", "equation", "calculate"),
        )

    # 关键优化：历史尺度判断
    def _is_local_trivia_query(self, text: str) -> bool:
        if self._matches_any(text, self.local_trivia_patterns):
            return True

        # 小范围实体（拒绝）
        small_scope_entities = (
            "university", "school", "college",
            "campus", "department", "institute",
            "company", "corporation", "office", "committee",
        )

        # 大范围实体（允许）
        large_scope_entities = (
            "country", "nation", "empire", "kingdom",
            "dynasty", "republic", "government",
            "president", "prime minister",
            "king", "queen",
        )

        position_terms = (
            "president", "chancellor", "dean",
            "principal", "rector", "headmaster",
            "founder", "ceo",
        )

        fact_request_terms = (
            "who was", "who is", "when was",
            "first", "founded", "established", "created",
        )

        # 如果是国家/帝国级 → 放行
        if self._contains_any(text, large_scope_entities) and not self._contains_any(text, small_scope_entities):
            return False

        # 小机构 + 职位 + fact → 拒绝
        if (
            self._contains_any(text, small_scope_entities)
            and self._contains_any(text, position_terms)
            and self._contains_any(text, fact_request_terms)
        ):
            return True

        # 明确本地指代
        local_markers = (
            "hong kong", "hkust", "my school",
            "our school", "this university", "local university",
        )

        if self._contains_any(text, local_markers) and self._contains_any(text, small_scope_entities):
            return True

        return False
