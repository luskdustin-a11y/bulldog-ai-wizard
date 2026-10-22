import ast
import pathlib
import unittest

class DashboardChatTests(unittest.TestCase):
    def test_chat_wired_to_local_model(self):
        dashboard = ast.parse(pathlib.Path("archer_dashboard.py").read_text())
        service = ast.parse(pathlib.Path("archer_chat_service.py").read_text())
        dashboard_calls = [n.func.id for n in ast.walk(dashboard) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        service_calls = [n.func.id for n in ast.walk(service) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]
        self.assertIn("answer", dashboard_calls)
        self.assertIn("chat_fn", service_calls)
        self.assertIn("respond", service_calls)
        self.assertIn("Thread", [n.func.attr for n in ast.walk(dashboard) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)])

    def test_ask_handler_present(self):
        tree = ast.parse(pathlib.Path("archer_dashboard.py").read_text())
        self.assertIn("ask", [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
