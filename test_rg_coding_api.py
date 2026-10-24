"""Tests for owner approval, staged integrity and RG API."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rg_coding_api import CodingDepartment
from rg_coding_department import RepairRejected

class CodingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.project = base / "project"
        self.project.mkdir()
        self.staging = base / "staging"
        (self.project / "sample.py").write_text("value = 1\n")
        self.api = CodingDepartment(self.project, self.staging)

    def test_propose_stage_verify(self):
        response = json.dumps({"path": "sample.py", "code": "value = 2\n"})
        with patch("rg_coding_department.chat", return_value=response):
            proposal = self.api.propose("sample.py", "Change value")
        with self.assertRaises(RepairRejected):
            self.api.stage(proposal, "NO")
        result = self.api.stage(proposal, "OWNER_APPROVED")
        self.assertEqual(result["state"], "STAGED_NOT_DEPLOYED")
        self.assertTrue(self.api.verify("sample.py"))
        self.assertEqual((self.project / "sample.py").read_text(), "value = 1\n")

    def test_source_change_blocks_verify(self):
        response = json.dumps({"path": "sample.py", "code": "value = 2\n"})
        with patch("rg_coding_department.chat", return_value=response):
            proposal = self.api.propose("sample.py", "Change value")
        self.api.stage(proposal, "OWNER_APPROVED")
        (self.project / "sample.py").write_text("value = 3\n")
        with self.assertRaises(RepairRejected):
            self.api.verify("sample.py")

if __name__ == "__main__":
    unittest.main()
