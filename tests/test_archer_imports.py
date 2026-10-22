import json
import tempfile
import unittest
from pathlib import Path
from archer_imports import stage_file

class ImportTests(unittest.TestCase):
    def test_stage_each_department(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for category in ("diagnostics", "hunting", "property", "hotshot", "finances", "stocks"):
                source = root / (category + ".json")
                source.write_text(json.dumps({"simulated": True}), encoding="utf-8")
                report = stage_file(category, source, root / "staged")
                self.assertTrue(Path(report["file"]).is_file())
                self.assertFalse(report["external_upload"])
                self.assertFalse(report["automated_analysis"])
                self.assertEqual(stage_file(category, source, root / "staged")["sha256"], report["sha256"])
    def test_reject_bad_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = root / "bad.json"
            source.write_text("not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                stage_file("finances", source, root / "staged")
            with self.assertRaises(ValueError):
                stage_file("invalid", source, root / "staged")
