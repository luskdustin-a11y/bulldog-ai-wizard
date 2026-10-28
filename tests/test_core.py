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

class MigrationSafetyTests(unittest.TestCase):
    def _env(self, d):
        return patch.object(core, "ROOT", Path(d)), patch.object(core, "DB", Path(d) / "core.db")

    def test_backup_created_and_notes_survive(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                core.add_note("Shop AI", "keep me")
                backup = core.enable_vault("correct horse battery")
                self.assertTrue(Path(backup).exists())
                self.assertIn(b"keep me", Path(backup).read_bytes())
                self.assertEqual(core.list_notes()[0]["text"], "keep me")
                core.lock_vault()

    def test_failed_migration_rolls_back_and_keeps_notes(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                core.add_note("Shop AI", "one")
                core.add_note("Shop AI", "two")
                calls = {"n": 0}
                real = core._encrypt
                def flaky(text):
                    calls["n"] += 1
                    if calls["n"] == 2:
                        raise OSError("disk error")
                    return real(text)
                with patch.object(core, "_encrypt", flaky), self.assertRaises(OSError):
                    core.enable_vault("correct horse battery")
                self.assertFalse(core.vault_enabled())
                self.assertEqual(sorted(n["text"] for n in core.list_notes()), ["one", "two"])
                self.assertEqual(len(list((Path(d) / "backups").glob("core-pre-vault-*.db"))), 1)

    def test_crash_after_vault_file_leaves_notes_readable(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                core.add_note("Shop AI", "plain")
                core.enable_vault("correct horse battery")
                with core.managed_connection() as db:
                    db.execute("INSERT INTO notes(department,text,created) VALUES('Shop AI','legacy plain','x')")
                self.assertEqual({n["text"] for n in core.list_notes()}, {"plain", "legacy plain"})
                core.lock_vault()

    def test_restore_backup_recovers_plaintext(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                core.add_note("Finances", "recover me")
                backup = core.enable_vault("correct horse battery")
                core.lock_vault()
                core.restore_backup(backup)
                self.assertFalse(core.vault_enabled())
                self.assertEqual(core.list_notes()[0]["text"], "recover me")
                self.assertTrue(list(Path(d).glob("core.db.replaced-*")))

    def test_restore_rejects_corrupt_backup(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                bad = Path(d) / "bad.db"
                bad.write_bytes(b"not a database")
                with self.assertRaises(Exception):
                    core.restore_backup(bad)

    def test_wrong_passphrase_and_short_passphrase(self):
        with tempfile.TemporaryDirectory() as d:
            r, b = self._env(d)
            with r, b:
                core.add_note("Shop AI", "x")
                with self.assertRaises(ValueError):
                    core.enable_vault("short")
                self.assertFalse(core.vault_enabled())
                core.enable_vault("correct horse battery")
                core.lock_vault()
                self.assertFalse(core.unlock_vault("incorrect passphrase"))

if __name__ == "__main__":
    unittest.main()
