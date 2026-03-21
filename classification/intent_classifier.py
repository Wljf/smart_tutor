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

Strict rules:
1. Choose homework_question for normal study requests, explanations, practice, quizzes, or subject questions.
2. Choose summary_request only if the user is asking to summarize the chat or conversation.
3. Choose unrelated_query only if the request is clearly outside tutoring or homework help.
4. Do not guess unrelated_query for normal school questions.

Return ONLY one label.

Conversation history:
{conversation_history or "No prior conversation."}

User query:
{query}
""".strip()

        response = self.llm_engine.invoke(
            system_prompt=(
                "You are a strict intent classifier for a homework tutoring assistant. "
                "Return only one valid label."
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
            "summarise chat",
            "give me a summary",
            "recap our conversation",
        )
        if any(phrase in normalized_query for phrase in summary_phrases):
            return "summary_request"

        unrelated_signals = (
            "plan a trip",
            "travel itinerary",
            "vacation",
            "restaurant recommendation",
            "movie recommendation",
            "betting",
            "celebrity gossip",
            "shopping advice",
        )
        if any(signal in normalized_query for signal in unrelated_signals):
            return "unrelated_query"

        homework_signals = (
            "explain",
            "solve",
            "calculate",
            "what is",
            "how do i solve",
            "help me with",
            "quiz me",
            "practice question",
            "practice questions",
            "homework",
            "assignment",
            "causes of",
            "effects of",
            "why did",
            "give me 3 questions",
            "teach me",
        )
        if any(signal in normalized_query for signal in homework_signals):
            return "homework_question"

        return None

    def _extract_label(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()
        compact = normalized.replace("-", "_").replace(" ", "_")

        if "summary_request" in compact or "summary" in normalized:
            return "summary_request"

        if "homework_question" in compact or "homework" in normalized:
            return "homework_question"

        if "unrelated_query" in compact or "unrelated" in normalized:
            return "unrelated_query"

        # Safer default: let the topic classifier decide the subject later.
        return "homework_question"
