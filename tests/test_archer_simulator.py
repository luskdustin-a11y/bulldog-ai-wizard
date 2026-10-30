import tempfile
import unittest
from archer_simulator import run_simulation

class SimulatorTests(unittest.TestCase):
    def test_unverified_simulator_does_not_claim_success(self):
        with tempfile.TemporaryDirectory() as folder:
            report = run_simulation(folder)
            self.assertEqual(report["status"], "NOT_VERIFIED")
            self.assertEqual(report["passed"], 0)
            self.assertEqual(report["verified_functional_tests"], 0)
            self.assertTrue(report["simulation_only"])
            self.assertFalse(report["real_hardware_connected"])
            self.assertFalse(report["external_accounts_connected"])
