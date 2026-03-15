from __future__ import annotations


class RejectResponse:
    def __init__(self, message: str) -> None:
        self.message = message

    def answer(self, *_args, **_kwargs) -> str:
        return self.message


class TaskRouter:
    def __init__(self, math_tutor, history_tutor, reject_message: str) -> None:
        self.math_tutor = math_tutor
        self.history_tutor = history_tutor
        self.reject_message = reject_message

    def route(self, topic: str):
        if topic == "math":
            return self.math_tutor
        if topic == "history":
            return self.history_tutor
        return RejectResponse(self.reject_message)
