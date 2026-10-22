import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import bulldawg_core as core
from archer_encrypted_backup import encrypt_backup, decrypt_backup

class EncryptedBackupTests(unittest.TestCase):
    def test_roundtrip_and_wrong_passphrase(self):
        try:
            import cryptography
        except ImportError:
            self.skipTest("Optional cryptography not installed")
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            with patch.object(core, "ROOT", folder), patch.object(core, "DB", folder / "core.db"):
                core.add_note("Supervisor", "encrypted test")
                sealed = folder / "sealed.archer"
                encrypt_backup(sealed, "strong-test-passphrase-123")
                self.assertNotIn(b"encrypted test", sealed.read_bytes())
                with self.assertRaises(Exception):
                    decrypt_backup(sealed, folder / "wrong.db", "incorrect-passphrase")
                result = decrypt_backup(sealed, folder / "restored.db", "strong-test-passphrase-123")
                self.assertEqual(result["notes"], 1)
