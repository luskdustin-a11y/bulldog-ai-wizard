"""Non-installing smoke tests for the Windows setup wizard."""
import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).with_name("bulldog_install_wizard.py")

class WizardSmokeTests(unittest.TestCase):
    def test_python_source_parses(self):
        ast.parse(SOURCE.read_text(encoding="utf-8"))
    def test_approval_gate_exists(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        methods = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertIn("run_installs", methods)
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                            and n.func.attr == "askyesno" for n in ast.walk(methods["run_installs"])))
    def test_no_install_on_import(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        guards = [n for n in tree.body if isinstance(n, ast.If) and
                  isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
                  and n.test.left.id == "__name__"]
        self.assertTrue(guards, "Wizard must have a main guard")

if __name__ == "__main__":
    unittest.main()
