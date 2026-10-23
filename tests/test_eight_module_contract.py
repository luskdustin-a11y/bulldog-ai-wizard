"""Cross-department contract and memory handoff tests (offline simulation only)."""
import unittest
from archer_department_hub import DEPARTMENTS, DepartmentHub, Request
from archer_module_event_router import ModuleEventRouter
from val_to_archie_bridge import ValEvent

class EightModuleContractTests(unittest.TestCase):
    def setUp(self):
        self.hub = DepartmentHub()
        self.router = ModuleEventRouter()
        self.names = sorted(DEPARTMENTS)
        self.assertEqual(len(self.names), 8)
        for name in self.names:
            self.hub.enroll("device-" + name, {name})
            self.hub.register(name, lambda question, name=name: name + ":" + question)
            self.router.enroll("module-" + name, {name})

    def test_each_module_loads_and_handles_own_request(self):
        self.assertEqual(self.hub.readiness()["missing_handlers"], [])
        for name in self.names:
            with self.subTest(department=name):
                response = self.hub.route(Request("device-" + name, name, "ping"))
                self.assertEqual(response["status"], "handled")
                self.assertEqual(response["answer"], name + ":ping")

    def test_cross_module_permissions_fail_closed(self):
        for name in self.names:
            other = next(item for item in self.names if item != name)
            with self.subTest(department=name):
                with self.assertRaises(PermissionError):
                    self.hub.route(Request("device-" + name, other, "ping"))
                with self.assertRaises(PermissionError):
                    self.router.deliver("module-" + name, other, self.event(name))

    @staticmethod
    def event(name):
        return ValEvent("event-" + name, "health", "memory", "healthy",
                        {"owner": name, "sequence": 1}, source="simulation",
                        timestamp="2026-10-23T00:00:00+00:00")

    def test_all_eight_module_memory_events_roundtrip(self):
        for name in self.names:
            with self.subTest(department=name):
                event = self.event(name)
                receipt = self.router.deliver("module-" + name, name, event)
                self.assertTrue(receipt["accepted"])
                stored = self.router.latest(name, "module-" + name, "memory")
                self.assertEqual(stored["details"], event.details)
                self.assertEqual(stored["source"], "simulation")
                self.assertTrue(self.router.deliver("module-" + name, name, event)["duplicate"])
        self.router.revoke("module-" + self.names[0])
        with self.assertRaises(PermissionError):
            self.router.deliver("module-" + self.names[0], self.names[0], self.event(self.names[0]))

if __name__ == "__main__":
    unittest.main()
