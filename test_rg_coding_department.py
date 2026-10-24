"""Unit tests for RG's guarded repair proposal path (no model/network needed)."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import rg_coding_department as rg

class RepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sample.py").write_text("value = 1\n", encoding="utf-8")

    def test_valid_proposal_does_not_modify_source(self):
        answer = json.dumps({"path": "sample.py", "code": "value = 2\n", "explanation": "Fix"})
        with patch.object(rg, "chat", return_value=answer):
            proposal = rg.propose_repair(self.root, "sample.py", "Correct value")
        self.assertEqual(proposal["status"], "PROPOSED_ONLY")
        self.assertFalse(proposal["tests_run"])
        self.assertIn("+value = 2", proposal["diff"])
        self.assertEqual((self.root / "sample.py").read_text(), "value = 1\n")

    def test_traversal_rejected(self):
        with self.assertRaises(rg.RepairRejected):
            rg.propose_repair(self.root, "../outside.py", "Fix")

    def test_invalid_python_rejected(self):
        answer = json.dumps({"path": "sample.py", "code": "def broken(:"})
        with patch.object(rg, "chat", return_value=answer):
            with self.assertRaises(rg.RepairRejected):
                rg.propose_repair(self.root, "sample.py", "Fix")

    def test_wrong_target_rejected(self):
        answer = json.dumps({"path": "other.py", "code": "value = 2"})
        with patch.object(rg, "chat", return_value=answer):
            with self.assertRaises(rg.RepairRejected):
                rg.propose_repair(self.root, "sample.py", "Fix")

if __name__ == "__main__":
    unittest.main()
