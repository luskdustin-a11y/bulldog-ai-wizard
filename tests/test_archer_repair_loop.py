import unittest
from archer_repair_loop import diagnose_and_repair

class RepairLoopTests(unittest.TestCase):
    def test_approved_repair_requires_verified_recheck(self):
        state = {"health": "failed"}
        def check(): return state["health"]
        def fix(): state["health"] = "ok"
        result = diagnose_and_repair("core", check, fix, owner_approved=True)
        self.assertTrue(result.verified)
        self.assertEqual(result.after, "ok")
    def test_unapproved_repair_never_runs(self):
        calls = []
        result = diagnose_and_repair("core", lambda: "failed", lambda: calls.append(1))
        self.assertFalse(result.verified)
        self.assertEqual(result.after, "failed")
        self.assertEqual(calls, [])
    def test_fake_repair_does_not_clear_red(self):
        result = diagnose_and_repair("core", lambda: "failed", lambda: None, owner_approved=True)
        self.assertFalse(result.verified)
        self.assertEqual(result.after, "failed")
    def test_exception_fails_closed(self):
        def broken(): raise RuntimeError("bad")
        result = diagnose_and_repair("core", broken)
        self.assertEqual(result.after, "failed")
        self.assertFalse(result.verified)

if __name__ == "__main__":
    unittest.main()
