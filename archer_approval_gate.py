"""Fail-closed, scoped software-change approval gate. No deployment is performed here."""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import secrets

class ApprovalDenied(PermissionError):
    pass

@dataclass(frozen=True)
class Proposal:
    issue: str
    artifact_sha256: str
    target: str

class ApprovalGate:
    """In-memory reference implementation. Integrate with durable audit/identity before production."""
    def __init__(self, owner_id: str, sister_id: str):
        self.owner_id = owner_id
        self.sister_id = sister_id
        self._delegations = {}
        self._approvals = {}
        self.audit = []

    def _log(self, event, **fields):
        self.audit.append({"at": datetime.now(timezone.utc).isoformat(), "event": event, **fields})

    def delegate(self, *, verified_actor: str, issue: str):
        if verified_actor != self.owner_id or not issue:
            raise ApprovalDenied("Only verified owner can delegate a specific issue")
        self._delegations[issue] = True
        self._log("delegated", issue=issue)

    def revoke(self, *, verified_actor: str, issue: str):
        if verified_actor != self.owner_id:
            raise ApprovalDenied("Only verified owner can revoke")
        self._delegations[issue] = False
        self._approvals = {k:v for k,v in self._approvals.items() if k[0] != issue}
        self._log("revoked", issue=issue)

    def approve(self, *, verified_actor: str, proposal: Proposal):
        if verified_actor != self.owner_id and not (
            verified_actor == self.sister_id and self._delegations.get(proposal.issue) is True
        ):
            raise ApprovalDenied("Verified owner or delegated sister required")
        if not proposal.issue or not proposal.target or len(proposal.artifact_sha256) != 64:
            raise ApprovalDenied("Invalid proposal")
        try:
            bytes.fromhex(proposal.artifact_sha256)
        except ValueError as exc:
            raise ApprovalDenied("Invalid digest") from exc
        key = (proposal.issue, proposal.target, proposal.artifact_sha256)
        self._approvals[key] = verified_actor
        self._log("approved", issue=proposal.issue, target=proposal.target,
                  digest=proposal.artifact_sha256, actor=verified_actor)

    def require_approval(self, *, proposal: Proposal, artifact: bytes):
        if not isinstance(artifact, bytes):
            raise ApprovalDenied("Artifact must be bytes")
        digest = hashlib.sha256(artifact).hexdigest()
        if not hmac.compare_digest(digest, proposal.artifact_sha256):
            raise ApprovalDenied("Artifact differs from approved bytes")
        key = (proposal.issue, proposal.target, proposal.artifact_sha256)
        if key not in self._approvals:
            raise ApprovalDenied("No verified approval for exact artifact and target")
        self._log("authorized_check", issue=proposal.issue, target=proposal.target)
        return True
