from __future__ import annotations

from llm.llm_engine import LLMEngine


class TopicClassifier:
    VALID_LABELS = ("math", "history", "other")

    def __init__(self, llm_engine: LLMEngine) -> None:
        self.llm_engine = llm_engine

    def classify(
        self,
        query: str,
        conversation_history: str = "",
        fallback_topic: str | None = None,
    ) -> str:
        rule_based_label = self._rule_based_override(query)
        if rule_based_label:
            return rule_based_label

        prompt = f"""
Classify the homework topic as exactly one label:
- math
- history
- other

Return only the label.

Conversation history:
{conversation_history or "No prior conversation."}

Most recent known topic:
{fallback_topic or "unknown"}

User query:
{query}
""".strip()

        response = self.llm_engine.invoke(
            system_prompt=(
                "You are a topic classifier for a homework tutoring assistant. "
                "Use the conversation history to resolve short follow-up questions."
            ),
            user_prompt=prompt,
        )
        extracted_label = self._extract_label(response)
        if extracted_label == "other" and fallback_topic in {"math", "history"}:
            if self._looks_like_follow_up(query):
                return fallback_topic
        return extracted_label

    def _rule_based_override(self, query: str) -> str | None:
        normalized_query = query.strip().lower()

        math_keywords = (
            "equation",
            "algebra",
            "geometry",
            "fraction",
            "solve",
            "calculate",
            "integral",
            "derivative",
            "probability",
            "math",
            "+",
            "-",
            "*",
            "/",
        )
        history_keywords = (
            "history",
            "war",
            "empire",
            "revolution",
            "president",
            "ancient",
            "medieval",
            "civilization",
            "historian",
            "treaty",
        )

        if any(keyword in normalized_query for keyword in math_keywords):
            return "math"
        if any(keyword in normalized_query for keyword in history_keywords):
            return "history"
        return None

    @staticmethod
    def _looks_like_follow_up(query: str) -> bool:
        normalized_query = query.strip().lower()
        follow_up_phrases = (
            "more",
            "another",
            "explain again",
            "practice",
            "quiz me",
            "one more",
            "give me 3",
            "can you continue",
        )
        return any(phrase in normalized_query for phrase in follow_up_phrases)

    def _extract_label(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()
        for label in self.VALID_LABELS:
            if label in normalized:
                return label
        return "other"
