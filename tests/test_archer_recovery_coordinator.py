"""Recovery integration tests using a disposable database."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sqlite3
import archer_recovery_coordinator as recovery

class RecoveryCoordinatorTests(unittest.TestCase):
    def test_snapshot_verify_restore_and_denial(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            db = root / "source.db"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, department TEXT, text TEXT)")
                conn.execute("INSERT INTO notes (department,text) VALUES ('Shop AI','test note')")
            # Replace the live database backup source with a disposable fixture.
            class Fixture:
                def __enter__(self):
                    self.connection = sqlite3.connect(db)
                    return self.connection
                def __exit__(self, *args):
                    self.connection.close()
            with patch("archer_backup.core.managed_connection", side_effect=lambda: Fixture()):
                snap = recovery.snapshot(root / "backups")
            source = snap["backup"]["file"]
            self.assertTrue(recovery.status(source)["ready"])
            dest = root / "restored.db"
            with self.assertRaises(PermissionError):
                recovery.recover(source, dest)
            result = recovery.recover(source, dest, approve=True)
            self.assertTrue(result["verified"]["valid"])
            self.assertEqual(result["verified"]["notes"], 1)
            with self.assertRaises(FileExistsError):
                recovery.recover(source, dest, approve=True)

    def test_corrupt_backup_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "corrupt.db"
            source.write_bytes(b"not sqlite")
            self.assertFalse(recovery.status(source)["ready"])
            with self.assertRaises((sqlite3.DatabaseError, ValueError)):
                recovery.recover(source, Path(directory) / "restored.db", approve=True)

if __name__ == "__main__":
    unittest.main()
