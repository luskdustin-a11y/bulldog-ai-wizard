"""Checks desktop entrypoint imports without requiring a display server."""
import ast
from pathlib import Path
import unittest

class DashboardTests(unittest.TestCase):
    def test_dashboard_parses(self):
        source = (Path(__file__).resolve().parents[1] / "archer_dashboard.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        self.assertTrue(any(isinstance(n, ast.ClassDef) and n.name == "ArcherDashboard" for n in tree.body))

    def test_explicitly_discloses_no_ai(self):
        source = (Path(__file__).resolve().parents[1] / "archer_dashboard.py").read_text(encoding="utf-8")
        self.assertIn("No AI model connected", source)
        self.assertIn("not an AI conversation", source)
