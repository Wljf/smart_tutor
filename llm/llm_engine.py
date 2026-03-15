from __future__ import annotations

from typing import Iterable

from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config import LLMSettings


class LLMEngine:
    """Central LangChain wrapper for all model calls."""

    def __init__(self, settings: LLMSettings) -> None:
        self.settings = settings
        self.model = self._build_model(settings)

    def _build_model(self, settings: LLMSettings):
        if settings.provider == "openai":
            if not settings.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY is required when TUTOR_LLM_PROVIDER=openai."
                )

            model_kwargs = {
                "model": settings.model_name,
                "temperature": settings.temperature,
                "api_key": settings.openai_api_key,
            }
            if settings.openai_base_url:
                model_kwargs["base_url"] = settings.openai_base_url

            return ChatOpenAI(**model_kwargs)

        if settings.provider == "ollama":
            return ChatOllama(
                model=settings.model_name,
                temperature=settings.temperature,
                base_url=settings.ollama_base_url,
            )

        raise ValueError(
            "Unsupported TUTOR_LLM_PROVIDER. Use 'openai' or 'ollama'."
        )

    def invoke(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Iterable[BaseMessage] | None = None,
    ) -> str:
        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=user_prompt))

        response = self.model.invoke(messages)
        return self._message_to_text(response)

    @staticmethod
    def _message_to_text(message: BaseMessage) -> str:
        if isinstance(message.content, str):
            return message.content.strip()
        if isinstance(message.content, list):
            text_parts = [
                chunk.get("text", "")
                for chunk in message.content
                if isinstance(chunk, dict)
            ]
            return "\n".join(part for part in text_parts if part).strip()
        return str(message.content).strip()

    @staticmethod
    def trim_history(history: list[BaseMessage], max_turns: int = 6) -> list[BaseMessage]:
        if max_turns <= 0:
            return []
        return history[-(max_turns * 2) :]
