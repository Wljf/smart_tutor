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
        parsed_level = self._extract_student_level(query)
        if parsed_level:
            self._student_level = parsed_level

    def get_student_level(self) -> str | None:
        return self._student_level

    def set_current_topic(self, topic: str) -> None:
        self._current_topic = topic

    def get_current_topic(self) -> str | None:
        return self._current_topic

    @classmethod
    def _extract_student_level(cls, query: str) -> str | None:
        normalized_query = query.strip().lower()
        year_pattern = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
        ordinal_year_pattern = (
            r"(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)"
            r"(?:-|\s)?year"
        )

        combined_patterns = [
            (
                rf"\b(university|college)\s+(year\s*{year_pattern})\b",
                lambda match: (
                    f"{cls._normalize_year_phrase(match.group(2))} {match.group(1)} student"
                ),
            ),
            (
                rf"\b(year\s*{year_pattern})\s+(university|college)\b",
                lambda match: (
                    f"{cls._normalize_year_phrase(match.group(1))} {match.group(2)} student"
                ),
            ),
            (
                rf"\b(university|college)\s+({ordinal_year_pattern})(?:\s+student)?\b",
                lambda match: (
                    f"{cls._normalize_year_phrase(match.group(2))} {match.group(1)} student"
                ),
            ),
            (
                rf"\b({ordinal_year_pattern})\s+(university|college)(?:\s+student)?\b",
                lambda match: (
                    f"{cls._normalize_year_phrase(match.group(1))} {match.group(2)} student"
                ),
            ),
            (
                rf"\b(high school|middle school|primary school)\s+"
                rf"(year\s*{year_pattern})\b",
                lambda match: (
                    f"{cls._normalize_year_phrase(match.group(2))} {match.group(1)} student"
                ),
            ),
        ]

        for pattern, formatter in combined_patterns:
            match = re.search(pattern, normalized_query, re.IGNORECASE)
            if match:
                return formatter(match)

        simple_patterns = [
            (
                rf"\b(year\s*{year_pattern})\b",
                lambda match: f"{cls._normalize_year_phrase(match.group(1))} student",
            ),
            (
                rf"\b({ordinal_year_pattern})(?:\s+student)?\b",
                lambda match: f"{cls._normalize_year_phrase(match.group(1))} student",
            ),
            (r"\b(grade\s*\d+)\b", lambda match: match.group(1)),
            (r"\b(class\s*\d+)\b", lambda match: match.group(1)),
            (r"\b(primary school)\b", lambda match: match.group(1)),
            (r"\b(middle school)\b", lambda match: match.group(1)),
            (r"\b(high school)\b", lambda match: match.group(1)),
            (r"\b(college)\b", lambda match: match.group(1)),
            (r"\b(university)\b", lambda match: match.group(1)),
        ]

        for pattern, formatter in simple_patterns:
            match = re.search(pattern, normalized_query, re.IGNORECASE)
            if match:
                return formatter(match)

        return None

    @staticmethod
    def _normalize_year_phrase(year_phrase: str) -> str:
        normalized = re.sub(r"\s+", " ", year_phrase.strip().lower())
        normalized = normalized.replace(" year", "-year")
        replacements = {
            "year 1": "first-year",
            "year one": "first-year",
            "first-year": "first-year",
            "year 2": "second-year",
            "year two": "second-year",
            "second-year": "second-year",
            "year 3": "third-year",
            "year three": "third-year",
            "third-year": "third-year",
            "year 4": "fourth-year",
            "year four": "fourth-year",
            "fourth-year": "fourth-year",
            "year 5": "fifth-year",
            "year five": "fifth-year",
            "fifth-year": "fifth-year",
            "year 6": "sixth-year",
            "year six": "sixth-year",
            "sixth-year": "sixth-year",
            "year 7": "seventh-year",
            "year seven": "seventh-year",
            "seventh-year": "seventh-year",
            "year 8": "eighth-year",
            "year eight": "eighth-year",
            "eighth-year": "eighth-year",
            "year 9": "ninth-year",
            "year nine": "ninth-year",
            "ninth-year": "ninth-year",
            "year 10": "tenth-year",
            "year ten": "tenth-year",
            "tenth-year": "tenth-year",
        }
        return replacements.get(normalized, normalized)
