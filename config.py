from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent
GUARDRAILS_DIR = BASE_DIR / "guardrails"


@dataclass(slots=True)
class LLMSettings:
    provider: str
    model_name: str
    temperature: float
    openai_api_key: str | None
    openai_base_url: str | None
    ollama_base_url: str


@dataclass(slots=True)
class AppConfig:
    llm: LLMSettings
    guardrails_config_path: Path
    reject_message: str


def load_config() -> AppConfig:
    provider = os.getenv("TUTOR_LLM_PROVIDER", "openai").strip().lower()
    default_model = "gpt-4o-mini" if provider == "openai" else "llama3.1"

    llm_settings = LLMSettings(
        provider=provider,
        model_name=os.getenv("TUTOR_MODEL", default_model).strip(),
        temperature=float(os.getenv("TUTOR_TEMPERATURE", "0.2")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
    )

    return AppConfig(
        llm=llm_settings,
        guardrails_config_path=GUARDRAILS_DIR / "rails_config.yml",
        reject_message="Sorry, I can only help with math or history homework questions.",
    )
