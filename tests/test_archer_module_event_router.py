import unittest
from archer_module_event_router import ModuleEventRouter
from val_to_archie_bridge import ValEvent

class ModuleRouterTests(unittest.TestCase):
    def test_multiple_modules_to_archie(self):
        router = ModuleEventRouter()
        router.enroll("val-unit", {"val"})
        router.enroll("laptop", {"supervisor"})
        a = ValEvent("1", "fault", "alternator", "warning", {"volts": 12.1})
        b = ValEvent("1", "health", "cpu", "healthy", {"temp_c": 52})
        self.assertTrue(router.deliver("val-unit", "val", a)["accepted"])
        self.assertTrue(router.deliver("laptop", "supervisor", b)["accepted"])
        self.assertEqual(router.latest("val", "val-unit", "alternator")["details"]["volts"], 12.1)
        self.assertEqual(router.latest("supervisor", "laptop", "cpu")["details"]["temp_c"], 52)
        self.assertTrue(router.deliver("val-unit", "val", a)["duplicate"])

    def test_deny_unauthorized_and_revoked(self):
        router = ModuleEventRouter()
        router.enroll("truck", {"val"})
        event = ValEvent("x", "fault", "wire", "warning", {})
        with self.assertRaises(PermissionError):
            router.deliver("truck", "finances", event)
        router.revoke("truck")
        with self.assertRaises(PermissionError):
            router.deliver("truck", "val", event)

if __name__ == "__main__":
    unittest.main()
