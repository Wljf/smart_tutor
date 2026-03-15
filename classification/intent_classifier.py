from __future__ import annotations

from llm.llm_engine import LLMEngine


class IntentClassifier:
    VALID_LABELS = (
        "homework_question",
        "summary_request",
        "unrelated_query",
    )

    def __init__(self, llm_engine: LLMEngine) -> None:
        self.llm_engine = llm_engine

    def classify(self, query: str, conversation_history: str = "") -> str:
        rule_based_label = self._rule_based_override(query)
        if rule_based_label:
            return rule_based_label

        prompt = f"""
Classify the user query as exactly one label:
- homework_question
- summary_request
- unrelated_query

Return only the label.

Conversation history:
{conversation_history or "No prior conversation."}

User query:
{query}
""".strip()

        response = self.llm_engine.invoke(
            system_prompt=(
                "You are an intent classifier for a homework tutoring assistant. "
                "Be strict and return only one valid label."
            ),
            user_prompt=prompt,
        )
        return self._extract_label(response)

    def _rule_based_override(self, query: str) -> str | None:
        normalized_query = query.strip().lower()

        summary_phrases = (
            "summarize our conversation so far",
            "summarise our conversation so far",
            "summarize the conversation",
            "summarise the conversation",
            "summarize chat",
        )
        if any(phrase in normalized_query for phrase in summary_phrases):
            return "summary_request"

        unrelated_signals = (
            "plan a trip",
            "travel",
            "vacation",
            "restaurant",
            "movie",
            "betting",
            "celebrity gossip",
        )
        if any(signal in normalized_query for signal in unrelated_signals):
            return "unrelated_query"

        return None

    def _extract_label(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()
        for label in self.VALID_LABELS:
            if label in normalized:
                return label
        return "unrelated_query"
