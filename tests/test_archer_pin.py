import tempfile
import unittest
from pathlib import Path
from archer_pin import PinGate

class PinTests(unittest.TestCase):
    def test_setup_unlock_and_lockout(self):
        with tempfile.TemporaryDirectory() as d:
            gate = PinGate(Path(d) / "pin.json")
            with self.assertRaises(ValueError):
                gate.setup("12345")
            gate.setup("4826")
            self.assertNotIn("4826", gate.path.read_text())
            gate.lock()
            self.assertFalse(gate.unlocked)
            self.assertFalse(gate.unlock("1111"))
            self.assertTrue(gate.unlock("4826"))
            gate.lock()
            for _ in range(5):
                self.assertFalse(gate.unlock("0000"))
            self.assertFalse(gate.unlock("4826"))
            self.assertGreater(gate.lock_until, 0)
