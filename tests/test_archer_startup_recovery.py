"""Regression checks for startup recovery safety."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from archer_startup_recovery import inspect_database, inspect_backups, startup_report

class StartupRecoveryTests(unittest.TestCase):
    def test_missing_database_does_not_start(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            report = startup_report(root / "missing.db", root / "backups")
            self.assertEqual(report["database"]["state"], "missing")
            self.assertFalse(report["database"]["safe_to_start"])
            self.assertEqual(report["action"], "require_owner_review")
            self.assertFalse(report["automatic_restore"])

    def test_healthy_database_starts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / "good.db"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, text TEXT)")
                conn.execute("INSERT INTO notes(text) VALUES ('memory')")
            report = startup_report(db, root / "backups")
            self.assertEqual(report["database"]["state"], "healthy")
            self.assertEqual(report["database"]["notes"], 1)
            self.assertEqual(report["action"], "continue")

    def test_corruption_blocks_start(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / "bad.db"
            db.write_bytes(b"not a database")
            report = startup_report(db, root / "backups")
            self.assertEqual(report["database"]["state"], "damaged")
            self.assertFalse(report["database"]["safe_to_start"])
            self.assertEqual(report["action"], "require_owner_review")

    def test_valid_backup_found_without_restoring(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            backup_dir = root / "backups"
            backup_dir.mkdir()
            db = backup_dir / "archer-valid.sqlite3"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, text TEXT)")
            report = startup_report(root / "missing.db", backup_dir)
            self.assertTrue(report["recovery_available"])
            self.assertFalse(report["automatic_restore"])
            self.assertFalse((root / "missing.db").exists())

if __name__ == "__main__":
    unittest.main()
