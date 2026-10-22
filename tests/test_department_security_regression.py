import unittest
from archer_department_hub import DepartmentHub, Request

class DepartmentSecurityTests(unittest.TestCase):
    def test_invalid_enrollment(self):
        for permissions in (None, "shop", [["shop"]], []):
            with self.subTest(permissions=repr(permissions)):
                with self.assertRaises(ValueError):
                    DepartmentHub().enroll("device", permissions)

    def test_missing_handler_fails_closed(self):
        hub = DepartmentHub()
        hub.enroll("device", {"shop"})
        self.assertEqual(hub.route(Request("device", "shop", "help"))["status"], "not-implemented")

    def test_permissions_and_revocation(self):
        hub = DepartmentHub()
        hub.enroll("device", {"shop"})
        hub.register("shop", lambda q: "ok")
        self.assertEqual(hub.route(Request("device", "shop", "help"))["status"], "handled")
        with self.assertRaises(PermissionError):
            hub.route(Request("device", "finances", "help"))
        hub.revoke("device")
        with self.assertRaises(PermissionError):
            hub.route(Request("device", "shop", "help"))

    def test_malformed_request(self):
        hub = DepartmentHub()
        with self.assertRaises(ValueError):
            hub.route(Request([], "shop", "help"))

if __name__ == "__main__":
    unittest.main()
