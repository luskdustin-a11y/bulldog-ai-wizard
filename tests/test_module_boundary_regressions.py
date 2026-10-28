"""Security and reliability regression checks for the Archie module event boundary."""
import unittest
from archer_module_event_router import ModuleEventRouter
from val_to_archie_bridge import ValEvent, ArchieBridge

class BoundaryRegressionTests(unittest.TestCase):
    def test_cross_module_isolation(self):
        r = ModuleEventRouter()
        r.enroll("val", {"val"})
        r.enroll("laptop", {"supervisor"})
        for module, dept in (("val", "val"), ("laptop", "supervisor")):
            ack = r.deliver(module, dept, ValEvent("shared", "health", "cpu", "healthy", {}))
            self.assertTrue(ack["accepted"])
            self.assertFalse(ack["duplicate"])
        self.assertEqual(len(r.inbox.events), 2)

    def test_conflicting_event_id_rejected(self):
        r = ModuleEventRouter()
        r.enroll("val", {"val"})
        r.deliver("val", "val", ValEvent("same", "fault", "battery", "warning", {"v": 12}))
        with self.assertRaises(ValueError):
            r.deliver("val", "val", ValEvent("same", "fault", "battery", "failed", {"v": 9}))

    def test_malformed_payload_and_unknown_kind(self):
        inbox = ArchieBridge()
        for payload in ('[]', '{"event_id": "x"}', 'not-json'):
            with self.assertRaises((ValueError, TypeError)):
                inbox.receive(payload)
        with self.assertRaises(ValueError):
            ValEvent("x", "arbitrary", "battery", "healthy", {}).encode()

    def test_revoked_module_cannot_send(self):
        r = ModuleEventRouter()
        r.enroll("module", {"val"})
        r.revoke("module")
        with self.assertRaises(PermissionError):
            r.deliver("module", "val", ValEvent("1", "health", "battery", "unknown", {}))

if __name__ == "__main__":
    unittest.main()
