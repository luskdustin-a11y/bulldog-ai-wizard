"""Archie protected-core reset planner.

Read-only plan and two-stage authorization protocol. Actual deletion deliberately
not implemented until authenticated owner UI, scoped backup, and rollback exist.
"""
from dataclasses import dataclass
import secrets

PROTECTED = frozenset({"archie_core", "owner_identity", "emergency_stop",
                       "security_policy", "reset_recovery"})
RESETTABLE = frozenset({"shop", "val", "hunting", "property", "hotshot",
                        "finances", "stocks", "supervisor_data", "settings", "cache"})

@dataclass(frozen=True)
class ResetPlan:
    request_id: str
    targets: tuple
    protected: tuple
    requires_double_confirmation: bool = True
    executable: bool = False

class ProtectedCoreReset:
    def __init__(self):
        self._requests = {}

    def plan(self, targets):
        targets = frozenset(targets)
        if not targets or not targets <= RESETTABLE:
            raise ValueError("Unknown or protected reset target")
        request_id = secrets.token_urlsafe(32)
        plan = ResetPlan(request_id, tuple(sorted(targets)), tuple(sorted(PROTECTED)))
        self._requests[request_id] = {"plan": plan, "confirmations": 0}
        return plan

    def confirm(self, request_id, *, owner_authenticated=False):
        record = self._requests.get(request_id)
        if record is None:
            raise PermissionError("Unknown reset request")
        # Boolean flags are not proof of owner identity; fail closed until
        # trusted owner authentication is integrated.
        raise PermissionError("Trusted owner authentication required; reset unavailable")

    def execute(self, request_id):
        raise PermissionError("Destructive reset disabled until backup, two authenticated confirmations and recovery are verified")
