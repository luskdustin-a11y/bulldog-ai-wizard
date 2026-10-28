import unittest
from archer_relay_acceptance import run_relay_acceptance

class RelayAcceptanceTests(unittest.TestCase):
    def test_queue_to_server_round_trip(self):
        result=run_relay_acceptance()
        self.assertTrue(result["passed"],result)
        self.assertEqual(result["delivered"],2)
        self.assertEqual(result["pending"],0)
