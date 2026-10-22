"""ARCHER unified AI and department integration contract.

Offline-only, deny-by-default, no model downloads or external network access.
Real model adapters and department implementations must be explicitly registered.
"""
from dataclasses import dataclass
from typing import Protocol

DEPARTMENTS = frozenset({"shop", "val", "hunting", "property", "hotshot", "finances", "stocks", "supervisor"})

class AIEngine(Protocol):
    def answer(self, question: str, department: str) -> str: ...

@dataclass(frozen=True)
class Request:
    device_id: str
    department: str
    question: str

class OfflineEngine:
    """Safe placeholder: never pretend an AI model is installed."""
    def answer(self, question, department):
        return ("ARCHER offline interface is available. "
                "A real local AI model is not installed or connected yet.")

class DepartmentHub:
    def __init__(self, engine=None):
        self.engine = engine if engine is not None else OfflineEngine()
        self._devices = {}
        self._handlers = {}

    def enroll(self, device_id, departments):
        allowed = frozenset(departments)
        if not isinstance(device_id, str) or not device_id.strip() or not allowed or not allowed <= DEPARTMENTS:
            raise ValueError("Invalid device or department permissions")
        if device_id in self._devices:
            raise ValueError("Device already enrolled")
        self._devices[device_id] = allowed

    def revoke(self, device_id):
        self._devices.pop(device_id, None)

    def register(self, department, handler):
        if department not in DEPARTMENTS or not callable(handler):
            raise ValueError("Invalid department handler")
        self._handlers[department] = handler

    def route(self, request):
        if not isinstance(request, Request) or request.department not in DEPARTMENTS:
            raise ValueError("Invalid request")
        if not isinstance(request.question, str) or not request.question.strip() or len(request.question) > 10000:
            raise ValueError("Invalid question")
        if request.department not in self._devices.get(request.device_id, frozenset()):
            raise PermissionError("Device not authorized for department")
        handler = self._handlers.get(request.department)
        if handler is None:
            return {"department": request.department, "status": "ai-interface-only",
                    "answer": self.engine.answer(request.question, request.department)}
        return {"department": request.department, "status": "handled",
                "answer": handler(request.question)}

    def readiness(self):
        return {"departments": sorted(DEPARTMENTS),
                "connected_handlers": sorted(self._handlers),
                "missing_handlers": sorted(DEPARTMENTS - self._handlers.keys()),
                "engine": type(self.engine).__name__}
