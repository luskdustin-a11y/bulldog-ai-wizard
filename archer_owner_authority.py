"""Archie core owner-authority gate.

No default approval. Approval is one-use, bound to an exact action and payload.
No AI module may issue an owner approval token on its own.
"""
import hashlib
import json
import secrets
from dataclasses import dataclass

@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str

class OwnerAuthority:
    def __init__(self):
        self._pending = {}
        self._approved = set()
        self._halted = False

    @staticmethod
    def _digest(action, payload):
        if not isinstance(action, str) or not action.strip():
            raise ValueError("Action required")
        try:
            canonical = json.dumps({"action": action, "payload": payload}, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("Action payload must be JSON serializable") from exc
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def request(self, action, payload):
        if self._halted:
            raise PermissionError("Emergency stop is active")
        digest = self._digest(action, payload)
        token = secrets.token_urlsafe(32)
        self._pending[token] = digest
        return token

    def approve(self, token, *, owner_authenticated=False):
        if self._halted:
            raise PermissionError("Emergency stop is active")
        # A caller-supplied boolean is not authentication. Fail closed until
        # a trusted owner authentication integration is implemented.
        raise PermissionError("Owner authentication integration not installed")
        digest = self._pending.pop(token, None)
        if digest is None:
            raise PermissionError("Unknown or already used request")
        self._approved.add((token, digest))

    def authorize(self, action, payload, token):
        if self._halted:
            return Decision(False, "Emergency stop")
        digest = self._digest(action, payload)
        key = (token, digest)
        if key not in self._approved:
            return Decision(False, "Specific owner approval required")
        self._approved.remove(key)
        return Decision(True, "Single-use owner approval consumed")

    def emergency_stop(self):
        self._halted = True
        self._pending.clear()
        self._approved.clear()

    @property
    def halted(self):
        return self._halted
