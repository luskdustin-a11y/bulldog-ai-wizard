"""Offline tests for complete-bundle integrity checks."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from archer_install_bundle import REQUIRED, verify_bundle

class BundleVerificationTests(unittest.TestCase):
    def make_bundle(self, path, *, corrupt=False, omit=None, unsafe=False):
        files = {name: name.encode() for name in REQUIRED if name != omit}
        hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
        if corrupt:
            hashes[next(iter(hashes))] = "0" * 64
        with zipfile.ZipFile(path, "w") as z:
            for name, data in files.items():
                z.writestr(name, data)
            if unsafe:
                z.writestr("../escape.txt", b"bad")
                hashes["../escape.txt"] = hashlib.sha256(b"bad").hexdigest()
            z.writestr("bundle-manifest.json", json.dumps({"sha256": hashes}))

    def test_valid_bundle(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bundle.zip"
            self.make_bundle(path)
            self.assertTrue(verify_bundle(path)["passed"])

    def test_corrupt_hash_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bundle.zip"
            self.make_bundle(path, corrupt=True)
            self.assertFalse(verify_bundle(path)["passed"])

    def test_missing_core_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bundle.zip"
            self.make_bundle(path, omit="archer_brain.py")
            self.assertFalse(verify_bundle(path)["passed"])

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bundle.zip"
            self.make_bundle(path, unsafe=True)
            self.assertFalse(verify_bundle(path)["passed"])

    def test_invalid_archive_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "bundle.zip"
            path.write_bytes(b"not a zip")
            self.assertFalse(verify_bundle(path)["passed"])

if __name__ == "__main__":
    unittest.main()
