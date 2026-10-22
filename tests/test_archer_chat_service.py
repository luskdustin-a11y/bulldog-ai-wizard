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
        reply = answer("Inspect my transmission", use_local_ai=True, chat_fn=local, models_fn=lambda: ['llama3.2'])
        self.assertEqual(reply.text, "Check the transmission fluid first.")

    def test_model_failure_safe(self):
        from archer_model import ModelUnavailable
        def unavailable(*args, **kwargs):
            raise ModelUnavailable("offline")
        reply = answer("Inspect my transmission", use_local_ai=True, chat_fn=unavailable, models_fn=lambda: ['llama3.2'])
        self.assertIn("unavailable", reply.text.lower())

    def test_serious_prompt(self):
        def local(message, prompt, model):
            self.assertIn("SERIOUS MODE", prompt)
            return "Stop and inspect brakes."
        self.assertEqual(answer("brake safety", use_local_ai=True, chat_fn=local, models_fn=lambda: ['llama3.2']).mode, "serious")

    def test_no_local_models_fails_closed(self):
        def unexpected(*args, **kwargs):
            self.fail("No model should be invoked")
        reply = answer("Inspect my transmission", use_local_ai=True, chat_fn=unexpected, models_fn=lambda: [])
        self.assertIn("unavailable", reply.text.lower())

    def test_selects_installed_model(self):
        def local(message, prompt, model):
            self.assertEqual(model, "gemma3:1b")
            return "Local response"
        reply = answer("Inspect transmission", use_local_ai=True, chat_fn=local, models_fn=lambda: ["gemma3:1b"])
        self.assertEqual(reply.text, "Local response")
