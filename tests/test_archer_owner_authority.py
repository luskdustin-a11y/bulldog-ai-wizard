import unittest
from archer_owner_authority import OwnerAuthority

class OwnerAuthorityTests(unittest.TestCase):
    def test_no_action_without_owner_approval(self):
        gate = OwnerAuthority()
        token = gate.request("change_setting", {"name": "mode", "value": 1})
        self.assertFalse(gate.authorize("change_setting", {"name": "mode", "value": 1}, token).allowed)
        with self.assertRaises(PermissionError):
            gate.approve(token)

    def test_spoofed_owner_boolean_is_rejected(self):
        gate = OwnerAuthority()
        token = gate.request("repair", {"module": "shop"})
        with self.assertRaises(PermissionError):
            gate.approve(token, owner_authenticated=True)
        self.assertFalse(gate.authorize("repair", {"module": "shop"}, token).allowed)

    def test_emergency_stop_revokes_requests(self):
        gate = OwnerAuthority()
        token = gate.request("repair", {"module": "shop"})
        gate.emergency_stop()
        self.assertFalse(gate.authorize("repair", {"module": "shop"}, token).allowed)
        with self.assertRaises(PermissionError):
            gate.request("repair", {})

if __name__ == "__main__":
    unittest.main()
