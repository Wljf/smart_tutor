from __future__ import annotations

from langchain_core.messages import BaseMessage

from llm.llm_engine import LLMEngine


class MathTutor:
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
You are a patient math homework tutor.

Rules:
- Only answer math homework questions.
- Adapt the explanation for {level_text}.
- Explain the solution in clear steps.
- If the student asks for practice or exercises, generate 3 short practice questions.
- Use concise reasoning steps that teach, not just the final answer.
- If the request is not about math homework, politely refuse.
""".strip()

        user_prompt = f"""
Help with this math homework request:
{query}
""".strip()

        trimmed_history = self.llm_engine.trim_history(history or [])
        return self.llm_engine.invoke(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            history=trimmed_history,
        )
