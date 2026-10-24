"""Owner-approved temporary exceptions with expiry and mandatory reevaluation.

Does not disable emergency stop, owner authentication or audit logging.
Uses a supplied monotonic clock for testability. No automatic permanent grants.
"""
from dataclasses import dataclass
import secrets
import time

PROTECTED = frozenset({"emergency_stop", "owner_authentication", "audit_logging",
                       "owner_approval", "intrusion_lockdown"})

@dataclass(frozen=True)
class TemporaryException:
    exception_id: str
    control: str
    reason: str
    expires_at: float
    status: str

class ExceptionWindow:
    def __init__(self, clock=None):
        self._clock = clock or time.monotonic
        self._active = {}

    def grant(self, control, reason, seconds, *, owner_approved=False):
        if owner_approved is not True:
            raise PermissionError("Specific authenticated owner approval required")
        if not isinstance(control, str) or not control.strip() or control in PROTECTED:
            raise PermissionError("Control cannot be temporarily bypassed")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Reason required")
        if type(seconds) not in (int, float) or not 1 <= seconds <= 3600:
            raise ValueError("Temporary window must be 1-3600 seconds")
        exception_id = secrets.token_urlsafe(24)
        item = TemporaryException(exception_id, control, reason, self._clock() + seconds, "temporary")
        self._active[exception_id] = item
        return item

    def active(self, exception_id):
        item = self._active.get(exception_id)
        return bool(item and self._clock() < item.expires_at)

    def revoke(self, exception_id):
        self._active.pop(exception_id, None)

    def reevaluate(self, exception_id, *, tests_passed, security_review_passed):
        item = self._active.get(exception_id)
        if item is None:
            raise KeyError("Unknown exception")
        result = {"exception_id": exception_id, "control": item.control,
                  "expired": not self.active(exception_id),
                  "recommended": "propose_permanent_change_for_owner_review"
                      if tests_passed is True and security_review_passed is True
                      else "restore_original_control",
                  "automatically_permanent": False}
        self.revoke(exception_id)
        return result
