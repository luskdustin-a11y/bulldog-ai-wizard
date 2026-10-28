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

class VaultTests(unittest.TestCase):
    def test_vault_encrypts_and_locks(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "core.db"
            with patch.object(core, "ROOT", Path(d)), patch.object(core, "DB", db):
                core.add_note("Finances", "old secret note")
                core.enable_vault("correct horse battery")
                self.assertTrue(core.health()["encrypted"])
                self.assertNotIn(b"old secret note", db.read_bytes())
                core.add_note("Finances", "new secret note")
                self.assertNotIn(b"new secret note", db.read_bytes())
                self.assertEqual(len(core.list_notes("Finances")), 2)
                core.lock_vault()
                with self.assertRaises(PermissionError):
                    core.list_notes()
                with self.assertRaises(PermissionError):
                    core.add_note("Finances", "x")
                self.assertFalse(core.unlock_vault("wrong passphrase!!"))
                self.assertTrue(core.unlock_vault("correct horse battery"))
                self.assertEqual(core.list_notes("Finances")[1]["text"], "old secret note")
                core.lock_vault()

if __name__ == "__main__":
    unittest.main()
