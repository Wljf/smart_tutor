from __future__ import annotations

from llm.llm_engine import LLMEngine


class TopicClassifier:
    VALID_LABELS = ("math", "history", "unclear", "other")

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
Classify the homework topic into EXACTLY ONE label:

- math
- history
- unclear
- other

Strict rules:
1. Choose math only if the query clearly involves numbers, formulas, equations, calculations, or math problem solving.
2. Choose history only if it clearly refers to historical events, people, periods, wars, causes, effects, or change over time in a historical sense.
3. If the request is vague, abstract, or could belong to multiple subjects, choose unclear.
4. If it is clearly outside math or history, choose other.
5. Do not guess.

Return ONLY one word: math, history, unclear, or other.

Conversation history:
{conversation_history or "No prior conversation."}

Most recent known topic:
{fallback_topic or "unknown"}

User query:
{query}
""".strip()

        response = self.llm_engine.invoke(
            system_prompt=(
                "You are a strict topic classifier for a homework tutoring assistant. "
                "You must follow classification rules and avoid guessing."
            ),
            user_prompt=prompt,
        )

        extracted_label = self._extract_label(response)

        if extracted_label in {"other", "unclear"} and fallback_topic in {"math", "history"}:
            if self._looks_like_follow_up(query) and len(query.split()) < 8:
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
            "statistics",
            "limit",
            "matrix",
            "percentage",
            "decimal",
            "multiply",
            "divide",
            "add",
            "subtract",
            "+",
            "-",
            "*",
            "/",
            "=",
        )

        history_keywords = (
            "history",
            "war",
            "world war",
            "wwi",
            "wwii",
            "empire",
            "revolution",
            "president",
            "king",
            "queen",
            "ancient",
            "medieval",
            "civilization",
            "treaty",
            "battle",
            "century",
            "dynasty",
            "historical",
            "roman empire",
            "french revolution",
        )

        history_phrases = (
            "talk about the history of",
            "learn about the history of",
            "explain the history of",
            "tell me about the history of",
            "what is the history of",
            "give me the history of",
            "let's talk about the history of",
        )

        change_patterns = (
            "change over time",
            "how did it change",
            "development of",
            "evolution of",
            "historical development",
            "how did it develop",
        )

        history_context_words = (
            "cause",
            "causes",
            "impact",
            "effects",
            "effect",
            "result",
            "results",
            "reason",
            "reasons",
        )

        history_anchor_words = (
            "war",
            "world war",
            "wwi",
            "wwii",
            "empire",
            "revolution",
            "history",
            "dynasty",
            "battle",
            "civilization",
            "king",
            "queen",
            "president",
            "treaty",
        )

        if any(keyword in normalized_query for keyword in math_keywords):
            return "math"

        if any(keyword in normalized_query for keyword in history_keywords):
            return "history"

        if any(phrase in normalized_query for phrase in history_phrases):
            return "history"

        if any(pattern in normalized_query for pattern in change_patterns):
            return "history"

        if any(word in normalized_query for word in history_context_words) and any(
            anchor in normalized_query for anchor in history_anchor_words
        ):
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
            "give me",
            "continue",
        )

        return any(phrase in normalized_query for phrase in follow_up_phrases)

    def _extract_label(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()
        compact = normalized.replace("-", "_").replace(" ", "_")

        if "unclear" in compact:
            return "unclear"
        if "math" in compact:
            return "math"
        if "history" in compact:
            return "history"
        if "other" in compact:
            return "other"

        return "unclear"
