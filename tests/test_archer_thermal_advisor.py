import unittest
from archer_thermal_advisor import advise_cooling

class ThermalAdvisorTests(unittest.TestCase):
    def test_normal_advice(self):
        result = advise_cooling(45, 50, case_c=30)
        self.assertEqual(result["state"], "normal")
        self.assertEqual(result["recommendations"], [])
        self.assertEqual(result["control_mode"], "advisory_only")

    def test_hot_and_low_fan_response(self):
        result = advise_cooling(83, 72, case_c=43, fan_percent=40)
        self.assertTrue(result["throttle_ai"])
        self.assertTrue(any("fan curve" in x for x in result["recommendations"]))
        self.assertTrue(any("dust filters" in x for x in result["recommendations"]))

    def test_critical_shutdown_is_only_requested(self):
        result = advise_cooling(96, 80)
        self.assertTrue(result["request_safe_shutdown"])
        self.assertEqual(result["control_mode"], "advisory_only")

    def test_invalid_optional_sensors(self):
        with self.assertRaises(ValueError):
            advise_cooling(60, 60, case_c=float("nan"))
        with self.assertRaises(ValueError):
            advise_cooling(60, 60, fan_percent=200)

if __name__ == "__main__":
    unittest.main()
