from __future__ import annotations

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
        cleaned_response = response.strip()
        normalized_response = cleaned_response.lower()

        if not cleaned_response:
            return "I could not produce a safe answer. Please try rephrasing your homework question."

        if topic is not None and topic not in self.allowed_subjects:
            return self.reject_message

        if any(pattern in normalized_response for pattern in self.blocked_patterns):
            return "I cannot provide that response safely. Please ask a math or history homework question."

        return cleaned_response
