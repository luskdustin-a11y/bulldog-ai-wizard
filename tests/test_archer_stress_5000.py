import unittest
from archer_stress_5000 import run_stress

class StressTests(unittest.TestCase):
    def test_five_thousand_messages_and_outages(self):
        result=run_stress()
        self.assertTrue(result["passed"],result)
        self.assertEqual(result["accepted"],5000)
        self.assertEqual(result["remaining"],0)
        self.assertGreater(result["simulated_outages"],0)
