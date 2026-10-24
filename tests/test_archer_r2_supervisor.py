"""R2 supervisor fail-closed behavior and bounded recovery tests."""
import tempfile
import unittest
from archer_r2_supervisor import R2Supervisor

class R2SupervisorTests(unittest.TestCase):
    def test_alerts_on_missing_verified_backup_and_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            report = R2Supervisor().assess(
                {"disk_total_gb": 100, "disk_free_gb": 3, "memory_percent": 94},
                backup_directory=directory, error_count=8)
        self.assertEqual(report["status"], "attention")
        self.assertEqual(report["backup_status"], "no_verified_backup")
        self.assertGreaterEqual(len(report["findings"]), 4)

    def test_recovery_denied_without_approval(self):
        calls = []
        with self.assertRaises(PermissionError):
            R2Supervisor().recover_transient(lambda: calls.append(1), lambda: True)
        self.assertEqual(calls, [])

    def test_recovery_stops_after_verified_success(self):
        calls = []
        result = R2Supervisor(max_retries=2).recover_transient(
            lambda: calls.append(1), lambda: len(calls) >= 2, approved=True)
        self.assertTrue(result["recovered"])
        self.assertEqual(result["attempts"], 2)

    def test_failed_recovery_enters_safe_mode(self):
        result = R2Supervisor(max_retries=1).recover_transient(
            lambda: None, lambda: False, approved=True)
        self.assertFalse(result["recovered"])
        self.assertTrue(result["safe_mode_required"])
        self.assertEqual(result["attempts"], 2)

    def test_emergency_stop_blocks_repairs(self):
        supervisor = R2Supervisor()
        supervisor.emergency_stop()
        self.assertTrue(supervisor.halted)
        calls = []
        with self.assertRaises(PermissionError):
            supervisor.recover_transient(lambda: calls.append(1), lambda: True, approved=True)
        self.assertEqual(calls, [])

    def test_stop_during_operation_blocks_success(self):
        supervisor = R2Supervisor(max_retries=2)
        calls = []
        def operation():
            calls.append(1)
            supervisor.emergency_stop()
        result = supervisor.recover_transient(operation, lambda: True, approved=True)
        self.assertFalse(result["recovered"])
        self.assertTrue(result["safe_mode_required"])
        self.assertEqual(len(calls), 1)

    def test_invalid_error_count_fails_closed(self):
        with self.assertRaises(ValueError):
            R2Supervisor().assess({}, error_count=-2)

if __name__ == "__main__":
    unittest.main()
