from __future__ import annotations

import sys
from collections.abc import MutableMapping
from pathlib import Path
import time

import gradio as gr

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from main import SmartTutorApp

SESSION_APPS: MutableMapping[str, SmartTutorApp] = {}


def _build_examples():
    return [
        ["What is 3 + 5?"],
        ["Explain the causes of World War I."],
        ["Give me 3 practice questions on fractions."],
        ["Quiz me on the French Revolution."],
        ["Explain change over time"],  # 测试 unclear
    ]


def _get_app(session_id: str) -> SmartTutorApp:
    app = SESSION_APPS.get(session_id)
    if app is None:
        app = SmartTutorApp()
        SESSION_APPS[session_id] = app
    return app

def chat(user_message, chat_history, request: gr.Request):
    session_id = request.session_hash

    if not user_message.strip():
        yield "", chat_history or [], "➤"
        return

    tutor_app = _get_app(session_id)
    history = chat_history or []

    # 用户消息
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": ""})

    # loading 状态
    yield "", history, "⏳"

    try:
        response, debug = tutor_app.handle_query(user_message)

        debug_line = f"""
<div style="font-size: 13px; color: gray;">
  <b>Topic:</b> {debug['topic']} &nbsp;&nbsp;
  <b>Guardrail:</b> {debug['guardrail']} &nbsp;&nbsp;
  <b>Decision:</b> {debug['decision']}
</div>
"""

        full_response = debug_line + "<br><br>" + response

    except Exception as exc:
        full_response = f"⚠️ Application error: {exc}"

    # streaming 输出（打字效果）
    current_text = ""
    for i, char in enumerate(full_response):
        current_text += char

        cursor = "▌" if i % 2 == 0 else ""
        history[-1]["content"] = current_text + cursor

        time.sleep(0.01)
        yield "", history, "⏳"

    # 最终输出（去掉光标）
    history[-1]["content"] = current_text
    yield "", history, "➤"


def clear_conversation(request: gr.Request):
    SESSION_APPS.pop(request.session_hash, None)
    return []


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* {
    font-family: 'Inter', sans-serif !important;
}

body {
    background: #f7f7f8;
}

.gradio-container {
    max-width: 900px !important;
    margin: auto;
}

#chatbot {
    height: 72vh;
    border-radius: 16px;
    border: none;
}

#input-container {
    display: flex;
    align-items: center;
    gap: 10px;
    background: white;
    padding: 10px 14px;
    border-radius: 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    transition: all 0.2s ease;
}

#input-container:focus-within {
    box-shadow: 0 4px 18px rgba(37, 99, 235, 0.25);
}

textarea {
    border: none !important;
    box-shadow: none !important;
    resize: none !important;
    font-size: 15px;
}

textarea:focus {
    outline: none !important;
}

#send-btn {
    min-width: 44px;
    height: 44px;
    border-radius: 999px;
    background: #2563eb !important;
    color: white !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    border: none;
    padding: 0 14px;
    transition: all 0.15s ease;
}

#send-btn:hover {
    background: #1d4ed8 !important;
    transform: scale(1.05);
}

#send-btn:active {
    transform: scale(0.92);
}
"""


# -----------------------------
# UI 构建
# -----------------------------
def build_ui():
    with gr.Blocks(css=CUSTOM_CSS, theme=gr.themes.Soft()) as demo:

        gr.Markdown("""
        # 🎓 Smart Tutor
        <center style='color:gray;'>Math & History Assistant</center>
        """)

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

        # 绑定事件
        send_button.click(
            chat,
            [message_box, chatbot],
            [message_box, chatbot, send_button]
        )

        message_box.submit(
            chat,
            [message_box, chatbot],
            [message_box, chatbot, send_button]
        )

    return demo


# -----------------------------
# Main
# -----------------------------
def main():
    demo = build_ui()
    demo.queue()
    demo.launch(share=True)


if __name__ == "__main__":
    main()
