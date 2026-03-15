from __future__ import annotations

from langchain_core.messages import BaseMessage

from llm.llm_engine import LLMEngine


class HistoryTutor:
    def __init__(self, llm_engine: LLMEngine) -> None:
        self.llm_engine = llm_engine

    def answer(
        self,
        query: str,
        history: list[BaseMessage] | None = None,
        student_level: str | None = None,
    ) -> str:
        level_text = student_level or "an unspecified school level"
        system_prompt = f"""
You are a careful history homework tutor.

Rules:
- Only answer history homework questions.
- Adapt the explanation for {level_text}.
- Explain events with context, causes, and consequences.
- If the student asks for practice or exercises, generate 3 history practice questions.
- Avoid obscure local trivia and refuse unrelated requests.
- Be clear, structured, and educational.
""".strip()

        user_prompt = f"""
Help with this history homework request:
{query}
""".strip()

        trimmed_history = self.llm_engine.trim_history(history or [])
        return self.llm_engine.invoke(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            history=trimmed_history,
        )
