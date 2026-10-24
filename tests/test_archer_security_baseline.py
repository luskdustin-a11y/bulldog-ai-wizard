import unittest
from archer_security_baseline import CONTROLS, security_readiness

class SecurityBaselineTests(unittest.TestCase):
    def test_all_ten_controls_present(self):
        self.assertEqual(len(CONTROLS), 10)
        self.assertEqual(len({item.key for item in CONTROLS}), 10)

    def test_unverified_system_never_marked_ready(self):
        report = security_readiness()
        self.assertFalse(report["ready_for_unattended_or_remote_control"])
        self.assertTrue(report["fail_closed"])
        self.assertIn("owner_passkey_authentication", report["blockers"])
        self.assertIn("independent_security_watchdog", report["blockers"])

if __name__ == "__main__":
    unittest.main()
