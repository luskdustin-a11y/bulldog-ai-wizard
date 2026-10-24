"""Bounded, auditable self-repair for ARCHER software processes.

Only restarts explicitly registered software components. Never edits code,
touches user memory, executes shell commands, or changes devices.
"""
from datetime import datetime, timezone
from time import monotonic

class RepairSupervisor:
    def __init__(self, *, max_attempts=3, cooldown_seconds=60, clock=monotonic):
        if max_attempts < 1 or cooldown_seconds < 0:
            raise ValueError("Invalid repair limits")
        self.max_attempts = max_attempts
        self.cooldown_seconds = cooldown_seconds
        self.clock = clock
        self.components = {}
        self.events = []

    def register(self, name, check, restart):
        if not isinstance(name, str) or not name or name in self.components:
            raise ValueError("Component name must be unique")
        if not callable(check) or not callable(restart):
            raise TypeError("Check and restart must be callable")
        self.components[name] = {"check": check, "restart": restart,
                                 "attempts": 0, "last_attempt": None}

    def inspect_and_repair(self, name):
        if name not in self.components:
            raise ValueError("Unknown component")
        component = self.components[name]
        try:
            healthy = bool(component["check"]())
        except Exception:
            healthy = False
        if healthy:
            component["attempts"] = 0
            return self._record(name, "healthy")
        if component["attempts"] >= self.max_attempts:
            return self._record(name, "manual_review_required")
        now = self.clock()
        if component["last_attempt"] is not None and now - component["last_attempt"] < self.cooldown_seconds:
            return self._record(name, "cooldown")
        component["attempts"] += 1
        component["last_attempt"] = now
        try:
            component["restart"]()
            repaired = bool(component["check"]())
        except Exception:
            repaired = False
        if repaired:
            component["attempts"] = 0
        return self._record(name, "repaired" if repaired else "repair_failed")

    def _record(self, name, status):
        event = {"component": name, "status": status,
                 "timestamp": datetime.now(timezone.utc).isoformat()}
        self.events.append(event)
        return event
