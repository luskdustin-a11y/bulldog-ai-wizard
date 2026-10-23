import unittest
from archer_self_repair import RepairSupervisor

class RepairTests(unittest.TestCase):
    def test_restarts_unhealthy_component(self):
        state = {"healthy": False, "restarts": 0}
        def restart():
            state["restarts"] += 1
            state["healthy"] = True
        supervisor = RepairSupervisor()
        supervisor.register("worker", lambda: state["healthy"], restart)
        self.assertEqual(supervisor.inspect_and_repair("worker")["status"], "repaired")
        self.assertEqual(state["restarts"], 1)

    def test_bounded_retries(self):
        calls = []
        supervisor = RepairSupervisor(max_attempts=2, cooldown_seconds=0)
        supervisor.register("worker", lambda: False, lambda: calls.append(1))
        self.assertEqual(supervisor.inspect_and_repair("worker")["status"], "repair_failed")
        self.assertEqual(supervisor.inspect_and_repair("worker")["status"], "repair_failed")
        self.assertEqual(supervisor.inspect_and_repair("worker")["status"], "manual_review_required")
        self.assertEqual(len(calls), 2)

    def test_cooldown(self):
        now = [10]
        supervisor = RepairSupervisor(cooldown_seconds=60, clock=lambda: now[0])
        supervisor.register("worker", lambda: False, lambda: None)
        supervisor.inspect_and_repair("worker")
        self.assertEqual(supervisor.inspect_and_repair("worker")["status"], "cooldown")

if __name__ == "__main__":
    unittest.main()
