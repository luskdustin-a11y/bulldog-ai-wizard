import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from archer_brain import respond, route
from archer_owner_authority import OwnerAuthority
from archer_pin import PinGate


class BrainIntegrationTests(unittest.TestCase):
    def test_routing(self):
        self.assertEqual(route("deer food plot"), "Hunting")
        self.assertEqual(route("engine repair"), "Shop AI")

    def test_memory_reaches_local_model_as_reference(self):
        with patch("archer_brain.core.list_notes", return_value=[{"text": "F250 has a 7.3 engine"}]), \
             patch("archer_brain.chat", return_value="Answer") as model:
            result = respond("engine repair", use_local_ai=True)
        self.assertEqual(result.mode, "local_ai")
        self.assertIn("F250 has a 7.3 engine", model.call_args.args[1])

    def test_no_ai_when_not_opted_in(self):
        with patch("archer_brain.chat") as model:
            respond("deer", use_local_ai=False)
        model.assert_not_called()


class OwnerApprovalIntegrationTests(unittest.TestCase):
    def test_pin_verified_approval_one_use_and_exact_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            gate = PinGate(Path(directory) / "owner_pin.json")
            gate.setup("9876")
            gate.lock()
            owner = OwnerAuthority()
            token = owner.request("change_setting", {"name": "mode", "value": 1})
            with self.assertRaises(PermissionError):
                owner.approve(token, owner_authenticated=True)
            with self.assertRaises(PermissionError):
                owner.approve_with_pin(token, "0000", gate)
            self.assertFalse(owner.authorize("change_setting", {"name": "mode", "value": 1}, token).allowed)
            owner.approve_with_pin(token, "9876", gate)
            self.assertFalse(owner.authorize("change_setting", {"name": "mode", "value": 2}, token).allowed)
            self.assertTrue(owner.authorize("change_setting", {"name": "mode", "value": 1}, token).allowed)
            self.assertFalse(owner.authorize("change_setting", {"name": "mode", "value": 1}, token).allowed)

    def test_emergency_stop_prevents_pin_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            gate = PinGate(Path(directory) / "owner_pin.json")
            gate.setup("9876")
            owner = OwnerAuthority()
            token = owner.request("repair", {})
            owner.emergency_stop()
            with self.assertRaises(PermissionError):
                owner.approve_with_pin(token, "9876", gate)


if __name__ == "__main__":
    unittest.main()
