"""Regression tests for event ID collisions and authenticated replay semantics."""
import secrets
import unittest
from archer_secure_transport import LocalReceiver, make_packet

class TransportHardeningTests(unittest.TestCase):
    def setUp(self):
        self.key=secrets.token_bytes(32)
        self.receiver=LocalReceiver(self.key,{"VAL","Phone"})
        self.event={"id":"same-id","source":"VAL","department":"Shop","payload":"original"}

    def test_exact_retry_is_idempotent(self):
        packet=make_packet(self.key,self.event)
        self.assertTrue(self.receiver.accept(packet))
        self.assertTrue(self.receiver.accept(packet))
        self.assertEqual(len(self.receiver.messages),1)

    def test_changed_payload_same_id_rejected(self):
        self.assertTrue(self.receiver.accept(make_packet(self.key,self.event)))
        altered={**self.event,"payload":"changed"}
        self.assertFalse(self.receiver.accept(make_packet(self.key,altered)))
        self.assertEqual(len(self.receiver.messages),1)

    def test_changed_source_same_id_rejected(self):
        self.assertTrue(self.receiver.accept(make_packet(self.key,self.event)))
        altered={**self.event,"source":"Phone"}
        self.assertFalse(self.receiver.accept(make_packet(self.key,altered)))

    def test_revoked_source_cannot_retry(self):
        packet=make_packet(self.key,self.event)
        self.assertTrue(self.receiver.accept(packet))
        self.receiver.allowed_sources.remove("VAL")
        self.assertFalse(self.receiver.accept(packet))
