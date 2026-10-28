import unittest
from archer_flow_simulation import STAGES, evaluate, simulate

class FlowSimulationTests(unittest.TestCase):
    def test_all_eight_and_fault_recovery(self):
        report = simulate()
        self.assertEqual(report["passed"], report["total"])
        self.assertEqual(len(report["healthy"]), 8)
        self.assertTrue(any(n["color"] == "red" for n in report["fault_injection"]))
        self.assertTrue(any(n["color"] == "yellow" for n in report["fault_injection"]))
        self.assertTrue(all(n["color"] == "blue" for n in report["after_simulated_repair"]))
    def test_bad_signals_fail_closed(self):
        with self.assertRaises(ValueError):
            evaluate({"core": "ok"})
        with self.assertRaises(ValueError):
            evaluate(dict.fromkeys(STAGES, "unknown"))

if __name__ == "__main__":
    unittest.main()
