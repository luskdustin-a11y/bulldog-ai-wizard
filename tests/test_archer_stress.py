"""Repeatable ARCHER stress tests. No network or device access."""
import concurrent.futures
import sqlite3
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bulldawg_core as core
from archer_brain import route, respond
from archer_security import hash_password, verify_password

class StressTests(unittest.TestCase):
    def test_1000_routes_and_responses(self):
        cases = [
            ("deer camera", "Hunting"),
            ("repair transmission", "Shop AI"),
            ("stock portfolio", "Stocks"),
            ("property renovation", "Property"),
            ("hotshot dispatch", "Hotshot"),
            ("budget expense", "Finances"),
            ("truck boost", "VAL"),
            ("system health", "Supervisor"),
        ]
        for i in range(1000):
            message, expected = cases[i % len(cases)]
            self.assertEqual(route(message), expected)
            self.assertEqual(respond(message).department, expected)

    def test_500_writes_and_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(core, "ROOT", Path(temp)), patch.object(core, "DB", Path(temp) / "core.db"):
                for i in range(500):
                    core.add_note("Hunting", f"Observation {i}")
                notes = core.list_notes("Hunting")
                self.assertEqual(len(notes), 500)
                self.assertEqual(len({n["id"] for n in notes}), 500)
                with sqlite3.connect(core.DB) as db:
                    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_100_concurrent_read_requests(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(core, "ROOT", Path(temp)), patch.object(core, "DB", Path(temp) / "core.db"):
                core.add_note("Shop AI", "first")
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
                    results = list(pool.map(lambda _: len(core.list_notes("Shop AI")), range(100)))
                self.assertEqual(results, [1] * 100)
                # Ensure SQLite handles have closed before Windows removes temp files.
                with sqlite3.connect(core.DB) as db:
                    self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_password_checks(self):
        encoded = hash_password("stress-test-private-password")
        for i in range(10):
            self.assertTrue(verify_password("stress-test-private-password", encoded))
            self.assertFalse(verify_password(f"incorrect-{i}", encoded))

if __name__ == "__main__":
    unittest.main()
