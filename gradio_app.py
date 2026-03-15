from __future__ import annotations

import sys
from collections.abc import MutableMapping
from pathlib import Path

import gradio as gr

# Allow running this file directly with:
# `python gradio_app.py`
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import SmartTutorApp


SESSION_APPS: MutableMapping[str, SmartTutorApp] = {}


def _build_examples() -> list[list[str]]:
    return [
        ["I am a year 1 student. What is 3 + 5?"],
        ["Explain the causes of World War I."],
        ["Give me 3 practice questions on fractions."],
        ["Quiz me on the French Revolution."],
        ["Summarize our conversation so far"],
        ["Plan my vacation in Japan"],
    ]


def _get_app(session_id: str) -> SmartTutorApp:
    app = SESSION_APPS.get(session_id)
    if app is None:
        app = SmartTutorApp()
        SESSION_APPS[session_id] = app
    return app


def chat(
    user_message: str,
    chat_history: list[dict[str, str]] | None,
    request: gr.Request,
):
    session_id = request.session_hash
    if not user_message.strip():
        return "", chat_history or []

    tutor_app = _get_app(session_id)
    history = chat_history or []

    try:
        assistant_message = tutor_app.handle_query(user_message)
    except Exception as exc:  # pragma: no cover - UI fallback
        assistant_message = f"Application error: {exc}"

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": assistant_message})
    return "", history


def clear_conversation(request: gr.Request):
    session_id = request.session_hash
    SESSION_APPS.pop(session_id, None)
    return []


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Smart Tutor") as demo:
        gr.Markdown(
            """
            # Smart Tutor
            A multi-turn homework tutoring assistant for math and history only.

            Supported features:
            - Multi-turn conversation
            - Homework filtering
            - Math and history routing
            - Difficulty-aware explanations
            - Exercise generation
            - Conversation summarization
            """
        )

        chatbot = gr.Chatbot(
            value=[],
            height=500,
            label="Homework Tutor",
        )

        with gr.Row():
            message_box = gr.Textbox(
                label="Your question",
                placeholder="Ask a math or history homework question...",
                lines=3,
                scale=8,
            )
            send_button = gr.Button("Send", variant="primary", scale=1)

        clear_button = gr.Button("Clear conversation")

        gr.Examples(
            examples=_build_examples(),
            inputs=message_box,
            label="Example prompts",
        )

        send_button.click(
            fn=chat,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot],
        )
        message_box.submit(
            fn=chat,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot],
        )
        clear_button.click(
            fn=clear_conversation,
            outputs=[chatbot],
        )

    return demo


def main() -> None:
    demo = build_ui()
    demo.launch(share=True)


if __name__ == "__main__":
    main()
