"""Tests for real local socket transport, still isolated from devices and internet."""
import secrets
import tempfile
import unittest
from pathlib import Path
from archer_durable_queue import DurableQueue
from archer_secure_transport import LocalReceiver, LoopbackServer, make_packet, send_loopback

class TransportTests(unittest.TestCase):
    def setUp(self):
        self.secret=secrets.token_bytes(32)
        self.receiver=LocalReceiver(self.secret,{"VAL","Phone"})
        self.server=LoopbackServer(self.receiver).start()

    def tearDown(self):
        self.server.close()

    def event(self):
        return {"id":"evt-1","source":"VAL","department":"VAL","payload":"EGT status"}

    def test_authenticated_delivery(self):
        self.assertTrue(send_loopback(self.server.port,make_packet(self.secret,self.event())))
        self.assertEqual(len(self.receiver.messages),1)

    def test_replay_idempotent(self):
        packet=make_packet(self.secret,self.event())
        self.assertTrue(send_loopback(self.server.port,packet))
        self.assertTrue(send_loopback(self.server.port,packet))
        self.assertEqual(len(self.receiver.messages),1)

    def test_wrong_key_rejected(self):
        self.assertFalse(send_loopback(self.server.port,make_packet(secrets.token_bytes(32),self.event())))

    def test_unauthorized_source_rejected(self):
        event=self.event()
        event["source"]="Unknown"
        self.assertFalse(send_loopback(self.server.port,make_packet(self.secret,event)))

    def test_tampering_rejected(self):
        packet=make_packet(self.secret,self.event())
        packet["envelope"]["payload"]="modified"
        self.assertFalse(send_loopback(self.server.port,packet))

    def test_expired_rejected(self):
        import time
        self.assertFalse(send_loopback(self.server.port,make_packet(self.secret,self.event(),timestamp=time.time()-500)))

    def test_durable_queue_to_socket(self):
        with tempfile.TemporaryDirectory() as directory:
            q=DurableQueue(Path(directory)/"queue.db")
            q.enqueue("VAL","VAL","test")
            self.assertEqual(q.flush({"VAL"},lambda event:send_loopback(self.server.port,make_packet(self.secret,event))),1)
            self.assertEqual(len(self.receiver.messages),1)
            self.assertEqual(q.pending(),[])
