import unittest
from archer_temporary_exceptions import ExceptionWindow

class ExceptionWindowTests(unittest.TestCase):
    def test_requires_owner_approval(self):
        with self.assertRaises(PermissionError):
            ExceptionWindow().grant("performance_limit", "diagnostics", 30)

    def test_critical_controls_cannot_be_bypassed(self):
        for control in ("emergency_stop", "owner_authentication", "owner_approval",
                        "audit_logging", "intrusion_lockdown"):
            with self.subTest(control=control), self.assertRaises(PermissionError):
                ExceptionWindow().grant(control, "diagnostics", 30, owner_approved=True)

    def test_expiration_and_reevaluation(self):
        now = [100.0]
        window = ExceptionWindow(clock=lambda: now[0])
        grant = window.grant("performance_limit", "test hardware", 20, owner_approved=True)
        self.assertTrue(window.active(grant.exception_id))
        now[0] = 121.0
        self.assertFalse(window.active(grant.exception_id))
        result = window.reevaluate(grant.exception_id, tests_passed=True, security_review_passed=True)
        self.assertEqual(result["recommended"], "propose_permanent_change_for_owner_review")
        self.assertFalse(result["automatically_permanent"])

    def test_failed_review_restores_original(self):
        window = ExceptionWindow()
        grant = window.grant("performance_limit", "diagnostics", 5, owner_approved=True)
        result = window.reevaluate(grant.exception_id, tests_passed=False, security_review_passed=True)
        self.assertEqual(result["recommended"], "restore_original_control")
        self.assertFalse(window.active(grant.exception_id))

if __name__ == "__main__":
    unittest.main()
