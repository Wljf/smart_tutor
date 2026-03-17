from __future__ import annotations

import re

from guardrails.input_guardrail import NeMoGuardrailsLayer


class OutputGuardrail:
    """Applies simple domain and safety checks to model outputs."""

    def __init__(self, guardrails_layer: NeMoGuardrailsLayer) -> None:
        policies = guardrails_layer.policies
        self.reject_message = policies.get(
            "reject_message",
            "Sorry, I can only help with math or history homework questions.",
        )
        self.blocked_patterns = [
            pattern.strip().lower()
            for pattern in policies.get("output_blocked_patterns", [])
            if pattern.strip()
        ]
        self.allowed_subjects = set(policies.get("allowed_subjects", ["math", "history"]))

    def validate(self, response: str, topic: str | None) -> str:
        cleaned_response = self._sanitize_response(response).strip()
        normalized_response = cleaned_response.lower()

        if not cleaned_response:
            return "I could not produce a safe answer. Please try rephrasing your homework question."

        if topic is not None and topic not in self.allowed_subjects:
            return self.reject_message

        if any(pattern in normalized_response for pattern in self.blocked_patterns):
            return "I cannot provide that response safely. Please ask a math or history homework question."

        return cleaned_response

    @staticmethod
    def _sanitize_response(response: str) -> str:
        cleaned = response or ""

        # Convert common display-style LaTeX wrappers into plain text so the UI
        # does not show raw control sequences.
        cleaned = re.sub(r"\\boxed\{([^{}]+)\}", r"\1", cleaned)
        cleaned = cleaned.replace(r"\[", "").replace(r"\]", "")
        cleaned = cleaned.replace(r"\(", "").replace(r"\)", "")
        cleaned = cleaned.replace("$$", "")
        cleaned = cleaned.replace("$", "")

        cleaned = re.sub(r"\n\s*\[\s*\n", "\n", cleaned)
        cleaned = re.sub(r"\n\s*\]\s*\n", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned
