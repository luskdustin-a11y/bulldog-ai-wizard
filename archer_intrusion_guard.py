"""R2 intrusion containment. Local-only, deny-by-default, no retaliation.

This policy engine does not claim to detect all compromises or isolate the OS.
"""
from dataclasses import dataclass
from datetime import datetime, timezone

EVENTS = frozenset({"failed_auth", "invalid_approval", "tamper_detected", "unexpected_remote_access"})
CRITICAL = frozenset({"tamper_detected", "unexpected_remote_access"})

@dataclass(frozen=True)
class Incident:
    event: str
    timestamp: str
    locked: bool
    reason: str

class IntrusionGuard:
    def __init__(self, *, auth_failure_limit=5):
        if type(auth_failure_limit) is not int or not 1 <= auth_failure_limit <= 20:
            raise ValueError("Invalid failure limit")
        self._limit = auth_failure_limit
        self._failures = 0
        self._locked = False
        self._incidents = []

    @property
    def locked(self):
        return self._locked

    def observe(self, event):
        if event not in EVENTS:
            raise ValueError("Unknown security event")
        if event in ("failed_auth", "invalid_approval"):
            self._failures += 1
        if event in CRITICAL or self._failures >= self._limit:
            self._locked = True
        incident = Incident(event, datetime.now(timezone.utc).isoformat(),
                            self._locked, "Security event requires owner review" if self._locked else "Monitored")
        self._incidents.append(incident)
        return incident

    def authorize_change(self):
        if self._locked:
            raise PermissionError("Security lockdown: system changes denied")
        # This is NOT owner authorization. All changes also need OwnerAuthority.
        return False

    def incidents(self):
        return tuple(self._incidents)

    def scan_report(self):
        return {"locked": self._locked, "events": len(self._incidents),
                "review_required": self._locked,
                "checks": ("authentication_failures", "approval_anomalies",
                           "tamper_alerts", "unexpected_remote_access"),
                "limitations": "Event-based detection only; no antivirus, network isolation, or OS-wide scan"}

    def reset(self, *args, **kwargs):
        raise PermissionError("Security lockdown requires separate trusted owner recovery")
