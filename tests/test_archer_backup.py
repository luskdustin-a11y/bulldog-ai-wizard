import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import bulldawg_core as core
from archer_backup import backup, verify, restore

class BackupTests(unittest.TestCase):
    def test_backup_verify_restore_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(core, "ROOT", root), patch.object(core, "DB", root / "core.db"):
                core.add_note("Hunting", "Simulated deer event")
                source = root / "backup.db"
                report = backup(source)
                self.assertFalse(report["encrypted"])
                self.assertEqual(verify(source)["notes"], 1)
                with self.assertRaises(FileExistsError):
                    backup(source)
                target = root / "recovered.db"
                with self.assertRaises(PermissionError):
                    restore(source, target)
                self.assertEqual(restore(source, target, approve=True)["notes"], 1)
                self.assertEqual(verify(target)["notes"], 1)
                with self.assertRaises(FileExistsError):
                    restore(source, target, approve=True)
