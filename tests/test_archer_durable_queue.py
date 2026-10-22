"""Durable queue tests, entirely offline."""
import tempfile
import unittest
from pathlib import Path
from archer_durable_queue import DurableQueue

class QueueTests(unittest.TestCase):
    def test_restart_recovery(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"events.db"
            q=DurableQueue(p)
            eid=q.enqueue("VAL","VAL","EGT warning")
            del q
            q=DurableQueue(p)
            self.assertEqual(q.pending()[0]["id"],eid)
            self.assertEqual(q.flush({"VAL"},lambda event: True),1)
            self.assertEqual(q.pending(),[])
            self.assertEqual(q.flush({"VAL"},lambda event: True),0)

    def test_failed_delivery_retained(self):
        with tempfile.TemporaryDirectory() as d:
            q=DurableQueue(Path(d)/"events.db")
            q.enqueue("Phone","Hunting","deer")
            self.assertEqual(q.flush({"Phone"},lambda event: False),0)
            self.assertEqual(len(q.pending()),1)
            self.assertEqual(q.flush({"Phone"},lambda event: True),1)

    def test_revoked_cannot_replay(self):
        with tempfile.TemporaryDirectory() as d:
            q=DurableQueue(Path(d)/"events.db")
            q.enqueue("VAL","VAL","secret")
            self.assertEqual(q.flush(set(),lambda event: True),0)
            self.assertEqual(q.pending(),[])
            self.assertEqual(q.flush({"VAL"},lambda event: True),0)

    def test_timeout_retry(self):
        with tempfile.TemporaryDirectory() as d:
            q=DurableQueue(Path(d)/"events.db")
            q.enqueue("VAL","VAL","status")
            def offline(event): raise ConnectionError("offline")
            self.assertEqual(q.flush({"VAL"},offline),0)
            self.assertEqual(len(q.pending()),1)
            self.assertEqual(q.flush({"VAL"},lambda event: True),1)

    def test_validation(self):
        with tempfile.TemporaryDirectory() as d:
            q=DurableQueue(Path(d)/"events.db")
            with self.assertRaises(ValueError): q.enqueue("VAL","VAL","")
            with self.assertRaises(ValueError): q.enqueue("VAL","VAL","x"*65537)
