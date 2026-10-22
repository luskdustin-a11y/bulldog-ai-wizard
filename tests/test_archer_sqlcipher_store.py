import unittest
from unittest.mock import patch
from archer_sqlcipher_store import open_encrypted

class EncryptedStoreTests(unittest.TestCase):
    def test_rejects_short_passphrase(self):
        with self.assertRaises(ValueError):
            open_encrypted("/tmp/archer-test.db", "short")

    def test_missing_driver_fails_closed(self):
        with patch("archer_sqlcipher_store._driver", side_effect=RuntimeError("missing")):
            with self.assertRaises(RuntimeError):
                open_encrypted("/tmp/archer-test.db", "long-safe-passphrase")

    def test_quoted_key_escaped(self):
        class FakeDB:
            def __init__(self): self.commands = []
            def execute(self, command):
                self.commands.append(command)
                return self
            def fetchone(self): return (0,)
            def commit(self): pass
            def close(self): pass
        class Driver:
            def __init__(self): self.db = FakeDB()
            def connect(self, *args, **kwargs): return self.db
        import tempfile
        from pathlib import Path
        driver = Driver()
        with tempfile.TemporaryDirectory() as tmp, patch("archer_sqlcipher_store._driver", return_value=driver):
            db = open_encrypted(Path(tmp) / "encrypted.db", "safe-password'quote")
            self.assertEqual(db.commands[0], "PRAGMA key = 'safe-password''quote'")
