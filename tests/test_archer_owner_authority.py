import unittest
from archer_owner_authority import OwnerAuthority

class OwnerAuthorityTests(unittest.TestCase):
    def test_no_action_without_owner_approval(self):
        gate = OwnerAuthority()
        token = gate.request("change_setting", {"name": "mode", "value": 1})
        self.assertFalse(gate.authorize("change_setting", {"name": "mode", "value": 1}, token).allowed)
        with self.assertRaises(PermissionError):
            gate.approve(token)

    def test_exact_single_use_permission(self):
        gate = OwnerAuthority()
        token = gate.request("repair", {"module": "shop"})
        gate.approve(token, owner_authenticated=True)
        self.assertFalse(gate.authorize("repair", {"module": "stocks"}, token).allowed)
        self.assertTrue(gate.authorize("repair", {"module": "shop"}, token).allowed)
        self.assertFalse(gate.authorize("repair", {"module": "shop"}, token).allowed)

    def test_emergency_stop_revokes_all(self):
        gate = OwnerAuthority()
        token = gate.request("repair", {"module": "shop"})
        gate.approve(token, owner_authenticated=True)
        gate.emergency_stop()
        self.assertFalse(gate.authorize("repair", {"module": "shop"}, token).allowed)
        with self.assertRaises(PermissionError):
            gate.request("repair", {})

if __name__ == "__main__":
    unittest.main()
