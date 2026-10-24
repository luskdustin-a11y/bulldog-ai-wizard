"""Regression checks for R2 preventive-maintenance rules."""
import unittest
from archer_preventive_maintenance import PreventiveMaintenance

class PreventiveMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.r2 = PreventiveMaintenance()

    def test_healthy_metrics(self):
        result = self.r2.inspect("shop", {"disk_free_pct": 70, "memory_used_pct": 20,
                                          "error_count": 0, "backup_age_hours": 2})
        self.assertEqual(result["status"], "no_thresholds_triggered")
        self.assertFalse(result["findings"])
        self.assertTrue(result["read_only"])

    def test_detects_all_four_weaknesses(self):
        result = self.r2.inspect("supervisor", {"disk_free_pct": 3, "memory_used_pct": 95,
                                                "error_count": 10, "backup_age_hours": 100})
        self.assertEqual(len(result["findings"]), 4)
        self.assertTrue(all(not item["automatic_repair_allowed"] for item in result["findings"]))

    def test_rejects_invalid_metrics(self):
        for metrics in ({"memory_used_pct": 101}, {"error_count": -1},
                        {"disk_free_pct": float("nan")}, {"error_count": "many"}):
            with self.subTest(metrics=metrics), self.assertRaises(ValueError):
                self.r2.inspect("shop", metrics)

    def test_rejects_invalid_component(self):
        with self.assertRaises(ValueError):
            self.r2.inspect("", {})

if __name__ == "__main__":
    unittest.main()
