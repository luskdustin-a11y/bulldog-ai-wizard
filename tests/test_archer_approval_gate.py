import hashlib
import unittest
from archer_approval_gate import ApprovalGate, ApprovalDenied, Proposal

class ApprovalGateTests(unittest.TestCase):
    def setUp(self):
        self.gate = ApprovalGate("owner", "sister")
        self.artifact = b"safe update"
        self.p = Proposal("issue-1", hashlib.sha256(self.artifact).hexdigest(), "phone")

    def test_missing_approval_denied(self):
        with self.assertRaises(ApprovalDenied):
            self.gate.require_approval(proposal=self.p, artifact=self.artifact)

    def test_spoofed_boolean_denied(self):
        with self.assertRaises(TypeError):
            self.gate.approve(verified_actor="intruder", proposal=self.p, owner_approved=True)
        with self.assertRaises(ApprovalDenied):
            self.gate.approve(verified_actor="intruder", proposal=self.p)

    def test_owner_approval_exact_bytes(self):
        self.gate.approve(verified_actor="owner", proposal=self.p)
        self.assertTrue(self.gate.require_approval(proposal=self.p, artifact=self.artifact))
        with self.assertRaises(ApprovalDenied):
            self.gate.require_approval(proposal=self.p, artifact=b"changed")

    def test_sister_requires_scope_and_revoke(self):
        with self.assertRaises(ApprovalDenied):
            self.gate.approve(verified_actor="sister", proposal=self.p)
        self.gate.delegate(verified_actor="owner", issue="issue-1")
        self.gate.approve(verified_actor="sister", proposal=self.p)
        self.gate.revoke(verified_actor="owner", issue="issue-1")
        with self.assertRaises(ApprovalDenied):
            self.gate.require_approval(proposal=self.p, artifact=self.artifact)

    def test_other_target_not_approved(self):
        self.gate.approve(verified_actor="owner", proposal=self.p)
        other = Proposal("issue-1", self.p.artifact_sha256, "laptop")
        with self.assertRaises(ApprovalDenied):
            self.gate.require_approval(proposal=other, artifact=self.artifact)

    def test_nonowner_cannot_delegate(self):
        with self.assertRaises(ApprovalDenied):
            self.gate.delegate(verified_actor="sister", issue="issue-1")

if __name__ == "__main__":
    unittest.main()
