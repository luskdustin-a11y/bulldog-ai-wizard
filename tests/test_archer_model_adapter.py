import unittest
from unittest.mock import patch
from archer_model_adapter import ModelAdapter

class ModelAdapterTests(unittest.TestCase):
    def test_cloud_blocked(self):
        with self.assertRaises(PermissionError):
            ModelAdapter(mode="cloud")

    def test_external_endpoint_blocked(self):
        with self.assertRaises(ValueError):
            ModelAdapter(endpoint="https://example.com")

    def test_empty_prompt_blocked(self):
        with self.assertRaises(ValueError):
            ModelAdapter().generate(" ")

    @patch("archer_model_adapter.urllib.request.urlopen")
    def test_local_generation(self, urlopen):
        urlopen.return_value.__enter__.return_value.read.return_value = b'{"response":"hello"}'
        self.assertEqual(ModelAdapter().generate("hi"), "hello")
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/generate")

if __name__ == "__main__":
    unittest.main()
