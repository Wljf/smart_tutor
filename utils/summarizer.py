from __future__ import annotations

from llm.llm_engine import LLMEngine


class ConversationSummarizer:
    def __init__(self, llm_engine: LLMEngine) -> None:
        self.llm_engine = llm_engine

    def summarize(self, transcript: str) -> str:
        if not transcript.strip():
            return "We have not discussed any homework questions yet."

        prompt = f"""
Summarize the conversation so far for the student.

Include:
- the main topic
- key explanations already given
- any follow-up areas that might still need clarification

Conversation transcript:
{transcript}
""".strip()

        return self.llm_engine.invoke(
            system_prompt=(
                "You summarize homework tutoring conversations clearly and briefly."
            ),
            user_prompt=prompt,
        )
