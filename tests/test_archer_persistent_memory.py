"""Regression tests for shared persistent memory."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import bulldawg_core
import archer_persistent_memory as memory

class PersistentMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.root_patch = patch.object(bulldawg_core, "ROOT", self.root)
        self.db_patch = patch.object(bulldawg_core, "DB", self.root / "core.db")
        self.root_patch.start()
        self.db_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.addCleanup(self.db_patch.stop)

    def test_memory_survives_separate_connections(self):
        item = memory.remember("Replace turbo seals", project="F250", kind="decision")
        matches = memory.recall(project="F250", query="turbo")
        self.assertEqual([row["id"] for row in matches], [item])
        self.assertEqual(matches[0]["content"], "Replace turbo seals")

    def test_projects_are_isolated_in_search(self):
        memory.remember("camera placement", project="Hunting")
        memory.remember("camera wiring", project="Truck")
        self.assertEqual(len(memory.recall(project="Hunting", query="camera")), 1)

    def test_invalid_memory_rejected(self):
        with self.assertRaises(ValueError):
            memory.remember(" ")
        with self.assertRaises(ValueError):
            memory.recall(limit=0)

if __name__ == "__main__":
    unittest.main()
