import json
import unittest
from unittest.mock import patch
from archer_model import chat, ModelUnavailable

class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self, size): return json.dumps({"message": {"content": "Local answer"}}).encode()

class ModelTests(unittest.TestCase):
    def test_local_model_reply(self):
        with patch("archer_model.http_response", return_value=FakeResponse()) as mock:
            self.assertEqual(chat("Hello", "You are ARCHER"), "Local answer")
            self.assertEqual(mock.call_args.args[0], "http://127.0.0.1:11434/api/chat")
            self.assertTrue(mock.call_args.kwargs['allow_loopback_http'])
            self.assertEqual(mock.call_args.kwargs['allowed_hosts'], {'127.0.0.1', 'localhost', '::1'})

    def test_blocks_external_servers(self):
        for url in ("https://example.com", "http://192.168.1.2:11434", "http://localhost.evil.com", "http://user@localhost:11434"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    chat("Hello", "system", base_url=url)

    def test_offline_failure_is_explicit(self):
        with patch("archer_model.http_response", side_effect=OSError("offline")):
            with self.assertRaises(ModelUnavailable):
                chat("Hello", "system")

    def test_malformed_model_messages_are_explicit_failures(self):
        for payload in [None, [], {'message': None}, {'message': 'bad'},
                        {'message': {'content': 12}}, {'message': {'content': ''}}]:
            response = FakeResponse()
            response.read = lambda size, value=payload: json.dumps(value).encode()
            with self.subTest(payload=payload), patch('archer_model.http_response', return_value=response):
                with self.assertRaises(ModelUnavailable):
                    chat('Hello', 'system')

    def test_oversized_model_message_is_rejected(self):
        response = FakeResponse()
        response.read = lambda size: b'x' * 2_000_001
        with patch('archer_model.http_response', return_value=response):
            with self.assertRaises(ModelUnavailable):
                chat('Hello', 'system')
