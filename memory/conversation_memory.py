from __future__ import annotations

import re

from langchain_classic.memory import ConversationBufferMemory

from langchain_core.messages import BaseMessage, HumanMessage


class ConversationMemoryManager:
    """Stores conversation turns and lightweight learner context."""

    def __init__(self) -> None:
        self._memory = ConversationBufferMemory(
            return_messages=True,
            input_key="user_input",
            output_key="assistant_response",
        )
        self._student_level: str | None = None
        self._current_topic: str | None = None

    def save_turn(self, user_message: str, assistant_response: str) -> None:
        self._memory.save_context(
            {"user_input": user_message},
            {"assistant_response": assistant_response},
        )

    def get_messages(self) -> list[BaseMessage]:
        history = self._memory.load_memory_variables({}).get("history", [])
        return history if isinstance(history, list) else []

    def get_transcript(self) -> str:
        lines: list[str] = []
        for message in self.get_messages():
            role = "User" if isinstance(message, HumanMessage) else "Assistant"
            lines.append(f"{role}: {message.content}")
        return "\n".join(lines)

    def update_student_level_from_query(self, query: str) -> None:
        patterns = [
            r"\b(year\s*\d+)\b",
            r"\b(grade\s*\d+)\b",
            r"\b(class\s*\d+)\b",
            r"\b(primary school)\b",
            r"\b(middle school)\b",
            r"\b(high school)\b",
            r"\b(college)\b",
            r"\b(university)\b",
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                self._student_level = match.group(1)
                return

    def get_student_level(self) -> str | None:
        return self._student_level

    def set_current_topic(self, topic: str) -> None:
        self._current_topic = topic

    def get_current_topic(self) -> str | None:
        return self._current_topic
