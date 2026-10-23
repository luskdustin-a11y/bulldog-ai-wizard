import ast
import pathlib
import unittest

class DashboardChatTests(unittest.TestCase):
    def test_chat_wired_to_local_model(self):
        tree = ast.parse(pathlib.Path("archer_dashboard.py").read_text())
        calls = [n.func.id for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertIn("answer_with_memory", calls)
        self.assertIn("respond", calls)
        self.assertIn("Thread", [n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)])

    def test_ask_handler_present(self):
        tree = ast.parse(pathlib.Path("archer_dashboard.py").read_text())
        names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        self.assertIn("ask", names)
