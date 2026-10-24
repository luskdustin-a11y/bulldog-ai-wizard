import unittest
from archer_comms_acceptance import run_acceptance

class CommunicationAcceptanceTests(unittest.TestCase):
    def test_complete_local_fleet(self):
        result=run_acceptance()
        self.assertTrue(result["passed"],result)
        self.assertEqual(result["delivered"],5)
        self.assertTrue(result["revocation_blocked"])
        self.assertEqual(result["pending"],0)
