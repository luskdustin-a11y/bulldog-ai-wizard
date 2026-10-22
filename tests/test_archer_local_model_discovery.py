import io
import unittest
from unittest.mock import patch
from archer_model import local_models, chat, ModelUnavailable

class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, count): return b'{"models":[{"name":"llama3.2:latest"},{"name":"private:cloud"},{"name":"gemma3:1b"}]}'

class LocalDiscoveryTests(unittest.TestCase):
    def test_local_models_only(self):
        with patch("archer_model.request.urlopen", return_value=FakeResponse()) as opener:
            self.assertEqual(local_models(), ["gemma3:1b", "llama3.2:latest"])
            self.assertIn("127.0.0.1", opener.call_args.args[0])

    def test_remote_url_blocked_without_request(self):
        with patch("archer_model.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                local_models("https://remote.example")
            opener.assert_not_called()

    def test_cloud_model_rejected_without_request(self):
        with patch("archer_model.request.urlopen") as opener:
            with self.assertRaises(ValueError):
                chat("hi", "private", model="some-model:cloud")
            opener.assert_not_called()

    def test_unavailable_server_fails_closed(self):
        with patch("archer_model.request.urlopen", side_effect=OSError("offline")):
            with self.assertRaises(ModelUnavailable):
                local_models()
