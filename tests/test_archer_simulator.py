import tempfile
import unittest
from archer_simulator import run_simulation

class SimulatorTests(unittest.TestCase):
    def test_all_departments_and_no_real_connections(self):
        with tempfile.TemporaryDirectory() as folder:
            report = run_simulation(folder)
            self.assertEqual(report["total"], 8)
            self.assertEqual(report["passed"], 8)
            self.assertTrue(report["simulation_only"])
            self.assertFalse(report["real_hardware_connected"])
            self.assertFalse(report["external_accounts_connected"])
    def test_repeatability(self):
        self.assertEqual(run_simulation(), run_simulation())
