"""Issue-scoped delegated technical approval. No email or deployment side effects."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from secrets import token_urlsafe

class State(str, Enum):
    PROPOSED = "proposed"
    DELEGATED = "delegated"
    APPROVED = "approved"
    REVOKED = "revoked"

@dataclass
class Delegation:
    issue_id: str
    owner_id: str
    advisor_id: str
    scope: str
    state: State = State.PROPOSED
    token: str = field(default_factory=lambda: token_urlsafe(32))
    events: list = field(default_factory=list)

    def _event(self, actor, action):
        self.events.append({"actor": actor, "action": action,
                            "at": datetime.now(timezone.utc).isoformat()})

    def delegate(self, actor, scope):
        if actor != self.owner_id or self.state != State.PROPOSED or scope != self.scope:
            raise PermissionError("Owner must authorize this exact issue and scope")
        self.state = State.DELEGATED
        self._event(actor, "delegate")

    def approve(self, actor, scope):
        if actor != self.advisor_id or self.state != State.DELEGATED or scope != self.scope:
            raise PermissionError("Advisor approval requires active matching delegation")
        self.state = State.APPROVED
        self._event(actor, "approve")

    def revoke(self, actor):
        if actor != self.owner_id:
            raise PermissionError("Only owner can revoke")
        self.state = State.REVOKED
        self._event(actor, "revoke")

    def can_execute(self, issue_id, scope):
        return self.state == State.APPROVED and self.issue_id == issue_id and self.scope == scope
