"""RG7 local task manager, central approval enforcement, and tamper-evident audit.

No tools are executed automatically. Only explicitly registered handlers can run.
"""
import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path

from archer_owner_authority import OwnerAuthority


class ActionController:
    def __init__(self, audit_path, authority=None):
        self.audit_path = Path(audit_path)
        self.authority = authority or OwnerAuthority()
        self.tasks = {}
        self.handlers = {}
        self._last_hash = self._verify_history()

    def _verify_history(self):
        previous = "0" * 64
        if not self.audit_path.exists():
            return previous
        with self.audit_path.open(encoding="utf-8") as stream:
            for line in stream:
                record = json.loads(line)
                digest = record.pop("hash")
                encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
                expected = hashlib.sha256(encoded.encode()).hexdigest()
                if record["previous"] != previous or digest != expected:
                    raise RuntimeError("Audit history integrity failure; controller locked")
                previous = digest
        return previous

    def _record(self, event, task_id, **fields):
        record = {"timestamp": datetime.now(timezone.utc).isoformat(),
                  "event": event, "task_id": task_id, "previous": self._last_hash,
                  **fields}
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
        record["hash"] = hashlib.sha256(encoded.encode()).hexdigest()
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            stream.flush()
        self._last_hash = record["hash"]

    def register(self, action, handler):
        if not callable(handler) or not isinstance(action, str) or not action:
            raise ValueError("Registered action and callable required")
        if action in self.handlers:
            raise ValueError("Action already registered")
        self.handlers[action] = handler

    def submit(self, department, action, payload):
        if self.authority.halted:
            raise PermissionError("Emergency stop active")
        if action not in self.handlers:
            raise PermissionError("Action has no registered handler")
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        task_id = secrets.token_hex(16)
        token = self.authority.request(action, payload)
        self.tasks[task_id] = {"department": department, "action": action,
                               "payload": payload.copy(), "token": token,
                               "state": "awaiting_approval"}
        self._record("submitted", task_id, department=department, action=action)
        return task_id

    def approve(self, task_id, pin, pin_gate):
        task = self.tasks[task_id]
        if task["state"] != "awaiting_approval":
            raise PermissionError("Task is not awaiting approval")
        self.authority.approve_with_pin(task["token"], pin, pin_gate)
        task["state"] = "approved"
        self._record("approved", task_id)

    def execute(self, task_id):
        task = self.tasks[task_id]
        if task["state"] != "approved":
            raise PermissionError("Task is not approved")
        decision = self.authority.authorize(task["action"], task["payload"], task["token"])
        if not decision.allowed:
            self._record("denied", task_id, reason=decision.reason)
            raise PermissionError(decision.reason)
        task["state"] = "running"
        self._record("started", task_id)
        try:
            result = self.handlers[task["action"]](**task["payload"])
        except Exception as exc:
            task["state"] = "failed"
            self._record("failed", task_id, error_type=type(exc).__name__)
            raise
        task["state"] = "completed"
        self._record("completed", task_id)
        return result

    def emergency_stop(self):
        self.authority.emergency_stop()
        for task in self.tasks.values():
            if task["state"] in ("awaiting_approval", "approved"):
                task["state"] = "cancelled"
        self._record("emergency_stop", "system")

    def status(self):
        return {task_id: {"department": t["department"], "action": t["action"],
                          "state": t["state"]} for task_id, t in self.tasks.items()}
