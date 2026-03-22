from __future__ import annotations

import sys
import time
from collections.abc import MutableMapping
from pathlib import Path

import gradio as gr

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import SmartTutorApp

SESSION_APPS: MutableMapping[str, SmartTutorApp] = {}


def _build_examples():
    return [
        ["Solve the equation: 2x + 5 = 15."],
        ["Explain the causes of World War I."],
        ["Find the derivative of x^2 + 3x."],
        ["Can you summarize our conversation so far?"],
    ]


def _get_app(session_id: str) -> SmartTutorApp:
    app = SESSION_APPS.get(session_id)
    if app is None:
        app = SmartTutorApp()
        SESSION_APPS[session_id] = app
    return app


def chat(user_message, chat_history, student_level, request: gr.Request):
    session_id = request.session_hash

    if not user_message.strip():
        yield (
            gr.update(
                value="",
                interactive=True,
                placeholder="Message Smart Tutor..."
            ),
            chat_history or [],
            gr.update(value="➤", interactive=True),
        )
        return

    tutor_app = _get_app(session_id)
    history = list(chat_history or [])

    history.append({"role": "user", "content": user_message})

    loading_bubble = """
<div class="assistant-loading">
  <div class="assistant-loading-title">Smart Tutor</div>
  <div class="assistant-loading-row">
    <span class="assistant-loading-dot"></span>
    <span class="assistant-loading-dot"></span>
    <span class="assistant-loading-dot"></span>
    <span class="assistant-loading-text">Thinking...</span>
  </div>
</div>
""".strip()

    history.append({"role": "assistant", "content": loading_bubble})

    yield (
        gr.update(
            value="",
            interactive=False,
            placeholder="Smart Tutor is thinking..."
        ),
        history,
        gr.update(value="...", interactive=False),
    )

    try:
        response, debug = tutor_app.handle_query(
            user_message,
            student_level=student_level,
        )

        debug_line = f"""
<div style="font-size: 12px; color: #6b7280; line-height: 1.4;">
  <b>Topic:</b> {debug['topic']} &nbsp;&nbsp;
  <b>Guardrail:</b> {debug['guardrail']} &nbsp;&nbsp;
  <b>Decision:</b> {debug['decision']} &nbsp;&nbsp;
  <b>Student level:</b> {student_level or "not set"}
</div>
""".strip()

        full_response = debug_line + "<br><br>" + response

    except Exception as exc:
        full_response = f"Application error: {exc}"

    history[-1]["content"] = ""

    chunk_size = 18
    for i in range(0, len(full_response), chunk_size):
        history[-1]["content"] = full_response[: i + chunk_size]
        yield (
            gr.update(
                value="",
                interactive=False,
                placeholder="Smart Tutor is thinking..."
            ),
            history,
            gr.update(value="...", interactive=False),
        )
        time.sleep(0.02)

    yield (
        gr.update(
            value="",
            interactive=True,
            placeholder="Message Smart Tutor..."
        ),
        history,
        gr.update(value="➤", interactive=True),
    )


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

body {
    background:
        radial-gradient(circle at top left, rgba(148, 163, 184, 0.08), transparent 26%),
        radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent 22%),
        linear-gradient(180deg, #f8fafc 0%, #f5f7fb 100%);
}

.gradio-container {
    max-width: 920px !important;
    margin: auto;
}

#app-shell {
    background: rgba(255, 255, 255, 0.90);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 28px;
    padding: 22px;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.06);
}


.hero-title {
    text-align: center;
    font-size: 34px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.hero-subtitle {
    text-align: center;
    font-size: 15px;
    color: #64748b;
    margin-bottom: 18px;
}

#student-level-wrap {
    margin-bottom: 12px;
}

#student-level-wrap .gradio-dropdown {
    border-radius: 16px !important;
}

#chatbot {
    height: 68vh;
    border-radius: 22px;
    border: 1px solid rgba(148, 163, 184, 0.16);
    overflow: hidden;
    background: linear-gradient(180deg, #f9fbfe 0%, #f3f7fc 100%);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
    outline: 1px solid rgba(203, 213, 225, 0.55);
}


#chatbot * {
    font-size: 14px !important;
    line-height: 1.5 !important;
}

#input-container {
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
    padding: 10px 14px;
    border-radius: 22px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    transition: all 0.2s ease;
    margin-top: 12px;
}

#input-container:focus-within {
    box-shadow: 0 12px 36px rgba(37, 99, 235, 0.16);
    border-color: rgba(37, 99, 235, 0.35);
}

textarea {
    border: none !important;
    box-shadow: none !important;
    resize: none !important;
    font-size: 14px !important;
    background: transparent !important;
}

textarea:focus {
    outline: none !important;
}

#send-btn {
    min-width: 46px;
    height: 46px;
    border-radius: 999px;
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border: none;
    padding: 0 14px;
    transition: all 0.15s ease;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.24);
}

#send-btn:hover {
    transform: scale(1.04);
    box-shadow: 0 10px 22px rgba(37, 99, 235, 0.30);
}

#send-btn:active {
    transform: scale(0.94);
}

.assistant-loading {
    display: inline-block;
    padding: 12px 14px;
    border-radius: 16px;
    background: linear-gradient(135deg, #f8fafc 0%, #eef4ff 100%);
    border: 1px solid #dbeafe;
    min-width: 180px;
}

.assistant-loading-title {
    font-size: 11px !important;
    font-weight: 600;
    color: #2563eb;
    margin-bottom: 6px;
    letter-spacing: 0.02em;
}

.assistant-loading-row {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #475569;
    font-size: 13px !important;
}

.assistant-loading-dot {
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: #2563eb;
    display: inline-block;
    animation: tutor-loading-bounce 1.2s infinite ease-in-out;
}

.assistant-loading-dot:nth-child(2) {
    animation-delay: 0.15s;
}

.assistant-loading-dot:nth-child(3) {
    animation-delay: 0.3s;
}

.assistant-loading-text {
    margin-left: 4px;
}

@keyframes tutor-loading-bounce {
    0%, 80%, 100% {
        transform: translateY(0);
        opacity: 0.45;
    }
    40% {
        transform: translateY(-4px);
        opacity: 1;
    }
}
"""


def build_ui():
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:
        with gr.Column(elem_id="app-shell"):
            gr.Markdown(
                """
<div class="hero-title">Smart Tutor</div>
<div class="hero-subtitle">Math and History homework help with student-level guidance</div>
""".strip()
            )

            with gr.Row(elem_id="student-level-wrap"):
                student_level = gr.Dropdown(
                    choices=[
                        "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6",
                        "Grade 7", "Grade 8", "Grade 9",
                        "Grade 10", "Grade 11", "Grade 12",
                        "College/University",
                    ],
                    allow_custom_value=True,
                    label="Student level",
                    info="Optional. You can also type your own level, such as Grade 6, Middle School, High School, or College.",
                    value=None,
                )

            chatbot = gr.Chatbot(
                value=[],
                elem_id="chatbot",
                type="messages",
            )

            with gr.Row(elem_id="input-container"):
                message_box = gr.Textbox(
                    placeholder="Message Smart Tutor...",
                    lines=1,
                    scale=8,
                    show_label=False,
                )
                send_button = gr.Button("➤", elem_id="send-btn")

            gr.Examples(
                examples=_build_examples(),
                inputs=message_box,
                label="Try examples",
            )

            send_button.click(
                chat,
                [message_box, chatbot, student_level],
                [message_box, chatbot, send_button],
            )

            message_box.submit(
                chat,
                [message_box, chatbot, student_level],
                [message_box, chatbot, send_button],
            )

    return demo


def main():
    demo = build_ui()
    demo.queue()
    demo.launch(share=True)


if __name__ == "__main__":
    main()
