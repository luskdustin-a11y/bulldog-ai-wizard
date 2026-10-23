import unittest
from archer_intrusion_guard import IntrusionGuard

class IntrusionGuardTests(unittest.TestCase):
    def test_repeated_failures_trigger_lockdown(self):
        guard = IntrusionGuard(auth_failure_limit=3)
        for _ in range(3):
            guard.observe("failed_auth")
        self.assertTrue(guard.locked)
        with self.assertRaises(PermissionError):
            guard.authorize_change()

    def test_tamper_triggers_immediate_lockdown(self):
        guard = IntrusionGuard()
        guard.observe("tamper_detected")
        self.assertTrue(guard.scan_report()["review_required"])

    def test_unknown_event_is_rejected(self):
        with self.assertRaises(ValueError):
            IntrusionGuard().observe("ignore_security")

    def test_cannot_self_unlock(self):
        guard = IntrusionGuard()
        guard.observe("unexpected_remote_access")
        with self.assertRaises(PermissionError):
            guard.reset()

    def test_no_implicit_owner_permission(self):
        self.assertFalse(IntrusionGuard().authorize_change())

if __name__ == "__main__":
    unittest.main()
