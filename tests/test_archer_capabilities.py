import unittest
from archer_capabilities import CAPABILITIES, get_capability, ready_for_release, report

class CapabilityTests(unittest.TestCase):
    def test_all_twelve_priorities_have_verification(self):
        self.assertEqual(len(CAPABILITIES), 12)
        self.assertEqual(len({c.id for c in CAPABILITIES}), 12)
        self.assertTrue(all(c.verification and c.next_step for c in CAPABILITIES))

    def test_unbuilt_features_not_marked_ready(self):
        self.assertFalse(ready_for_release())
        self.assertEqual(get_capability("android").status, "planned")
        self.assertEqual(get_capability("security").status, "blocked")

    def test_json_safe_report(self):
        import json
        self.assertEqual(len(json.loads(json.dumps(report()))), 12)
