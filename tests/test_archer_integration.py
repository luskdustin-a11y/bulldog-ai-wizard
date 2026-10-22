import unittest
from archer_brain import route, respond
from archer_security import hash_password, verify_password

class IntegrationTests(unittest.TestCase):
    def test_routes(self):
        self.assertEqual(route("check the deer camera"), "Hunting")
        self.assertEqual(route("repair the transmission"), "Shop AI")
        self.assertEqual(route("hello"), "Supervisor")

    def test_no_false_integration_claims(self):
        self.assertIn("not connected yet", respond("check deer camera").text)

    def test_serious(self):
        self.assertEqual(respond("truck brake danger").mode, "serious")

    def test_password(self):
        encoded = hash_password("a-long-private-password")
        self.assertNotIn("a-long-private-password", encoded)
        self.assertTrue(verify_password("a-long-private-password", encoded))
        self.assertFalse(verify_password("wrong-password", encoded))
