import unittest
from archer_supervisor import Supervisor

class SupervisorTests(unittest.TestCase):
    def test_default_reports_unready(self):
        s=Supervisor()
        result=s.status()
        self.assertFalse(result["ready"])
        self.assertEqual(result["ready_count"],0)
        self.assertIn("val",s.required_work())

    def test_dependency_blocks_ready(self):
        s=Supervisor()
        s.report("dashboard",implemented=True,tested=True,healthy=True)
        self.assertFalse(s.status()["components"]["dashboard"]["ready"])
        self.assertEqual(s.status()["components"]["dashboard"]["blocked_by"],["brain"])

    def test_dependency_restores_ready(self):
        s=Supervisor()
        s.report("brain",implemented=True,tested=True,healthy=True)
        s.report("dashboard",implemented=True,tested=True,healthy=True)
        self.assertTrue(s.status()["components"]["dashboard"]["ready"])

    def test_unverified_health_rejected(self):
        s=Supervisor()
        with self.assertRaises(ValueError):
            s.report("val",implemented=False,tested=False,healthy=True)

    def test_unknown_component_rejected(self):
        s=Supervisor()
        with self.assertRaises(ValueError):
            s.report("unknown",implemented=True,tested=True,healthy=True)
