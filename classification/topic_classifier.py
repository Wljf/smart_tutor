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
1. Only choose "math" if the question clearly involves mathematical concepts or problem solving.
2. Only choose "history" if it clearly refers to historical events, people, or time periods.
3. If the question is vague, abstract, or involves multiple disciplines, and there is no clear disciplinary orientation or indication → Select "unclear".
4. If it is clearly outside math/history → choose "other".
5. DO NOT guess.

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
          "equation", "algebra", "geometry", "fraction",
          "solve", "calculate", "integral", "derivative",
          "probability", "statistics", "limit", "matrix",
          "+", "-", "*", "/", "="
      )

      history_keywords = (
          "history", "war", "empire", "revolution",
          "president", "king", "queen", "ancient",
          "medieval", "civilization", "treaty",
          "battle", "century", "year", "historical"
      )
、
      if any(keyword in normalized_query for keyword in math_keywords):
          return "math"

      if any(keyword in normalized_query for keyword in history_keywords):
          return "history"

      # 新增：抽象历史表达（关键）
      history_phrases = (
          "talk about the history of",
          "learn about the history of",
          "explain the history of",
          "tell me about the history of",
          "what is the history of",
          "give me the history of",
          "let's talk about the history of",
      )

      if any(phrase in normalized_query for phrase in history_phrases):
          return "history"

      # 变化也被认为是history
      change_patterns = (
          "change over time",
          "how did it change",
          "development of",
          "evolution of",
          "historical development",
          "how did it develop",
      )

      if any(pattern in normalized_query for pattern in change_patterns):
          return "history"

      # FIX 1：宽松历史识别（解决 WWI 问题）
      if "war" in normalized_query or "world war" in normalized_query:
          return "history"

      history_context_words = (
          "cause", "causes", "impact", "effects",
          "result", "results", "reason", "reasons"
      )

      if any(w in normalized_query for w in history_context_words):
          if any(h in normalized_query for h in (
              "war", "empire", "revolution", "history",
              "dynasty", "battle", "civilization"
          )):
              return "history"
      return None

    @staticmethod
    def _looks_like_follow_up(query: str) -> bool:
        normalized_query = query.strip().lower()

        follow_up_phrases = (
            "more", "another", "explain again",
            "practice", "quiz me", "one more",
            "give me", "continue"
        )

        return any(phrase in normalized_query for phrase in follow_up_phrases)

    def _extract_label(self, raw_response: str) -> str:
        normalized = raw_response.strip().lower()

        if "unclear" in normalized:
            return "unclear"

        for label in ("math", "history", "other"):
            if label in normalized:
                return label

        # 默认拒绝猜测
        return "unclear"
