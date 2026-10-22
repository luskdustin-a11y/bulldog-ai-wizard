import tempfile
import unittest
from pathlib import Path
from archer_pin import PinGate
from archer_install_preflight import simulate_install, REPORTED_HP

class SimulatedLaptopSecurityTests(unittest.TestCase):
    def test_hp_report_and_pin_restart(self):
        report = simulate_install(REPORTED_HP)
        self.assertTrue(report["simulation_only"])
        self.assertFalse(report["device_scanned"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "owner_pin.json"
            gate = PinGate(path)
            gate.setup("4826")
            gate.lock()
            for _ in range(5):
                self.assertFalse(gate.unlock("0000"))
            restarted = PinGate(path)
            self.assertFalse(restarted.unlock("4826"))
            self.assertGreater(restarted.lock_until, 0)
            self.assertNotIn("4826", path.read_text())
