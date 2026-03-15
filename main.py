from __future__ import annotations

import sys
from pathlib import Path

# Allow running this file directly with:
# `python smart_tutor/main.py`
if __package__ is None or __package__ == "":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from  agents.history_tutor import HistoryTutor
from  agents.math_tutor import MathTutor
from  classification.intent_classifier import IntentClassifier
from  classification.topic_classifier import TopicClassifier
from  config import load_config
from  guardrails.input_guardrail import InputGuardrail, NeMoGuardrailsLayer
from  guardrails.output_guardrail import OutputGuardrail
from  llm.llm_engine import LLMEngine
from  memory.conversation_memory import ConversationMemoryManager
from  router.task_router import TaskRouter
from  utils.summarizer import ConversationSummarizer


class SmartTutorApp:
    """Coordinates the tutoring pipeline end to end."""

    def __init__(self) -> None:
        self.config = load_config()
        self.guardrails_layer = NeMoGuardrailsLayer(self.config.guardrails_config_path)
        self.input_guardrail = InputGuardrail(self.guardrails_layer)
        self.output_guardrail = OutputGuardrail(self.guardrails_layer)
        self.llm_engine = LLMEngine(self.config.llm)
        self.memory = ConversationMemoryManager()
        self.intent_classifier = IntentClassifier(self.llm_engine)
        self.topic_classifier = TopicClassifier(self.llm_engine)
        self.math_tutor = MathTutor(self.llm_engine)
        self.history_tutor = HistoryTutor(self.llm_engine)
        self.router = TaskRouter(
            math_tutor=self.math_tutor,
            history_tutor=self.history_tutor,
            reject_message=self.config.reject_message,
        )
        self.summarizer = ConversationSummarizer(self.llm_engine)

    def handle_query(self, user_query: str) -> str:
        self.memory.update_student_level_from_query(user_query)

        input_decision = self.input_guardrail.validate(user_query)
        if not input_decision.allowed:
            self.memory.save_turn(user_query, input_decision.response)
            return input_decision.response

        conversation_history = self.memory.get_transcript()
        intent = self.intent_classifier.classify(
            query=user_query,
            conversation_history=conversation_history,
        )

        if intent == "summary_request":
            response = self.summarizer.summarize(conversation_history)
            safe_response = self.output_guardrail.validate(
                response=response,
                topic=None,
            )
            self.memory.save_turn(user_query, safe_response)
            return safe_response

        if intent == "unrelated_query":
            self.memory.save_turn(user_query, self.config.reject_message)
            return self.config.reject_message

        topic = self.topic_classifier.classify(
            query=user_query,
            conversation_history=conversation_history,
            fallback_topic=self.memory.get_current_topic(),
        )

        tutor = self.router.route(topic)
        response = tutor.answer(
            query=user_query,
            history=self.memory.get_messages(),
            student_level=self.memory.get_student_level(),
        )
        safe_response = self.output_guardrail.validate(response=response, topic=topic)

        if topic in {"math", "history"}:
            self.memory.set_current_topic(topic)

        self.memory.save_turn(user_query, safe_response)
        return safe_response


def run_cli() -> None:
    app = SmartTutorApp()

    print("Smart Tutor CLI")
    print("Ask a math or history homework question. Type 'exit' to quit.\n")
    print("Example prompts:")
    print("- I am a year 1 student. What is 3 + 5?")
    print("- Explain why the Roman Empire fell.")
    print("- Give me 3 practice questions on fractions.")
    print("- Summarize our conversation so far\n")

    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            print("Assistant: Goodbye!")
            break

        try:
            response = app.handle_query(user_query)
        except Exception as exc:  # pragma: no cover - CLI fallback
            response = f"Application error: {exc}"

        print(f"Assistant: {response}\n")


if __name__ == "__main__":
    run_cli()
