import unittest
from archer_chat_service import answer

class ChatIntegrationTests(unittest.TestCase):
    def test_offline_fallback(self):
        reply = answer("How do I inspect my transmission?")
        self.assertEqual(reply.department, "Shop AI")
        self.assertIn("Routing", reply.text)

    def test_real_adapter_result(self):
        def local(message, prompt, model):
            self.assertIn("transmission", message)
            self.assertIn("ARCHER", prompt)
            return "Check the transmission fluid first."
        reply = answer("Inspect my transmission", use_local_ai=True, chat_fn=local)
        self.assertEqual(reply.text, "Check the transmission fluid first.")

    def test_model_failure_safe(self):
        from archer_model import ModelUnavailable
        def unavailable(*args, **kwargs):
            raise ModelUnavailable("offline")
        reply = answer("Inspect my transmission", use_local_ai=True, chat_fn=unavailable)
        self.assertIn("unavailable", reply.text.lower())

    def test_serious_prompt(self):
        def local(message, prompt, model):
            self.assertIn("SERIOUS MODE", prompt)
            return "Stop and inspect brakes."
        self.assertEqual(answer("brake safety", use_local_ai=True, chat_fn=local).mode, "serious")
