"""R2 health adapter: warning and missing-data regression tests."""
import unittest
from archer_r2_health_monitor import check_local_health

class R2HealthMonitorTests(unittest.TestCase):
    def test_warning_from_actual_health_shape(self):
        report = check_local_health({"disk_total_gb": 100, "disk_free_gb": 4,
                                     "memory_percent": 96})
        self.assertEqual(report["status"], "attention")
        self.assertEqual(len(report["findings"]), 2)
        self.assertIn("backup_age_hours", report["metrics_unavailable"])
        self.assertTrue(report["read_only"])

    def test_unknown_is_not_healthy(self):
        report = check_local_health({"disk_total_gb": 100, "disk_free_gb": 60,
                                     "memory_percent": None})
        self.assertEqual(report["status"], "insufficient_data")
        self.assertIn("memory_used_pct", report["metrics_unavailable"])

    def test_no_disk_total_does_not_divide_by_zero(self):
        report = check_local_health({"disk_total_gb": 0, "disk_free_gb": 0})
        self.assertIn("disk_free_pct", report["metrics_unavailable"])

if __name__ == "__main__":
    unittest.main()
