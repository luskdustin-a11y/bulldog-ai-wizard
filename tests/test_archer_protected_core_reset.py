import unittest
from archer_protected_core_reset import ProtectedCoreReset, PROTECTED

class ProtectedCoreResetTests(unittest.TestCase):
    def test_reset_plan_preserves_core(self):
        plan = ProtectedCoreReset().plan(["shop", "settings", "cache"])
        self.assertTrue(plan.requires_double_confirmation)
        self.assertFalse(plan.executable)
        self.assertTrue(PROTECTED.issubset(set(plan.protected)))

    def test_protected_core_cannot_be_targeted(self):
        with self.assertRaises(ValueError):
            ProtectedCoreReset().plan(["archie_core"])

    def test_no_destructive_action_even_with_spoofed_boolean(self):
        reset = ProtectedCoreReset()
        plan = reset.plan(["cache"])
        with self.assertRaises(PermissionError):
            reset.confirm(plan.request_id, owner_authenticated=True)
        with self.assertRaises(PermissionError):
            reset.execute(plan.request_id)

if __name__ == "__main__":
    unittest.main()
