import unittest
from dataclasses import asdict
from val_to_archie_bridge import ArchieBridge, ValEvent

class BridgeTests(unittest.TestCase):
    def test_val_to_archie_and_duplicate(self):
        bridge = ArchieBridge()
        event = ValEvent("evt-1", "power", "alternator", "warning",
                         {"voltage": 12.1}, source="simulation", timestamp="2026-10-22T21:00:00Z")
        payload = event.encode()
        self.assertEqual(bridge.receive(payload), {"event_id": "evt-1", "accepted": True, "duplicate": False})
        self.assertEqual(bridge.component_state("alternator")["details"]["voltage"], 12.1)
        self.assertTrue(bridge.receive(payload)["duplicate"])

    def test_reject_bad_source(self):
        with self.assertRaises(ValueError):
            ValEvent("evt-2", "fault", "amp", "failed", {}, source="imagined").encode()

    def test_reject_conflicting_id(self):
        bridge = ArchieBridge()
        bridge.receive(ValEvent("same", "fault", "amp", "failed", {}).encode())
        with self.assertRaises(ValueError):
            bridge.receive(ValEvent("same", "fault", "amp", "healthy", {}).encode())

if __name__ == "__main__":
    unittest.main()
