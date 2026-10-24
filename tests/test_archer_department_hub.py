import unittest
from archer_department_hub import DepartmentHub, Request

class DepartmentHubTests(unittest.TestCase):
    def test_unenrolled_device_denied(self):
        with self.assertRaises(PermissionError):
            DepartmentHub().route(Request("phone","shop","help"))

    def test_department_permission_isolated(self):
        hub=DepartmentHub()
        hub.enroll("phone",{"hunting"})
        with self.assertRaises(PermissionError):
            hub.route(Request("phone","finances","balance"))

    def test_handler_connected(self):
        hub=DepartmentHub()
        hub.enroll("phone",{"shop"})
        hub.register("shop",lambda question:"processed: "+question)
        result=hub.route(Request("phone","shop","check injector"))
        self.assertEqual(result["answer"],"processed: check injector")
        self.assertEqual(result["status"],"handled")

    def test_missing_ai_model_not_faked(self):
        hub=DepartmentHub()
        hub.enroll("phone",{"val"})
        result=hub.route(Request("phone","val","diagnose truck"))
        self.assertEqual(result["status"],"not-implemented")
        self.assertIn("No working department handler",result["answer"])

    def test_revocation_immediate(self):
        hub=DepartmentHub()
        hub.enroll("phone",{"shop"})
        hub.revoke("phone")
        with self.assertRaises(PermissionError):
            hub.route(Request("phone","shop","hello"))

    def test_all_departments_listed(self):
        hub=DepartmentHub()
        self.assertEqual(len(hub.readiness()["missing_handlers"]),8)
