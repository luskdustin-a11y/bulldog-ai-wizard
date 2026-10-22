import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import bulldawg_core as core

class CoreTests(unittest.TestCase):
    def test_health_and_notes(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(core, "ROOT", Path(d)), patch.object(core, "DB", Path(d) / "core.db"):
                self.assertEqual(core.health()["status"], "ok")
                self.assertFalse(core.health()["encrypted"])
                core.add_note("Shop AI", "Inspect F-250")
                self.assertEqual(core.list_notes("Shop AI")[0]["text"], "Inspect F-250")
                with self.assertRaises(ValueError):
                    core.add_note("Invalid", "text")

if __name__ == "__main__":
    unittest.main()
