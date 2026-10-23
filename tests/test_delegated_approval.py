import unittest
from delegated_approval import Delegation, State

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.d = Delegation("issue-1", "owner", "natasha", "repair-parser")

    def test_advisor_cannot_approve_without_delegation(self):
        with self.assertRaises(PermissionError):
            self.d.approve("natasha", "repair-parser")

    def test_authorized_approval(self):
        self.d.delegate("owner", "repair-parser")
        self.d.approve("natasha", "repair-parser")
        self.assertTrue(self.d.can_execute("issue-1", "repair-parser"))
        self.assertFalse(self.d.can_execute("issue-2", "repair-parser"))

    def test_wrong_actor_or_scope(self):
        with self.assertRaises(PermissionError):
            self.d.delegate("natasha", "repair-parser")
        self.d.delegate("owner", "repair-parser")
        with self.assertRaises(PermissionError):
            self.d.approve("natasha", "disable-safety")

    def test_owner_revoke(self):
        self.d.delegate("owner", "repair-parser")
        self.d.approve("natasha", "repair-parser")
        self.d.revoke("owner")
        self.assertFalse(self.d.can_execute("issue-1", "repair-parser"))

if __name__ == "__main__":
    unittest.main()
