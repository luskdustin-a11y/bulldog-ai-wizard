import unittest
from archer_pc_thermal import decide_thermal

class ThermalPolicyTests(unittest.TestCase):
    def test_normal(self):
        result = decide_thermal(45, 55)
        self.assertEqual((result.state, result.fan_percent), ("normal", 40))
        self.assertFalse(result.throttle_ai)
    def test_warm(self):
        self.assertEqual(decide_thermal(66, 60).fan_percent, 75)
    def test_hot(self):
        result = decide_thermal(82, 70)
        self.assertTrue(result.throttle_ai)
        self.assertFalse(result.request_safe_shutdown)
        self.assertEqual(result.fan_percent, 100)
    def test_critical(self):
        result = decide_thermal(70, 96)
        self.assertTrue(result.request_safe_shutdown)
        self.assertEqual(result.state, "critical")
    def test_missing_and_invalid(self):
        for bad in (None, float("nan"), float("inf"), 200, True):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                decide_thermal(bad, 40)
    def test_bad_thresholds(self):
        with self.assertRaises(ValueError):
            decide_thermal(60, 60, warning_c=100, critical_c=90)

if __name__ == "__main__":
    unittest.main()
