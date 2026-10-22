import unittest
from archer_persona import SYSTEM_NAME, VOICE_PROFILE, ResponseContext, build_system_prompt

class ArcherPersonaTests(unittest.TestCase):
    def test_identity(self):
        self.assertEqual(SYSTEM_NAME, "ARCHER")
        self.assertIn("Original performance", VOICE_PROFILE["note"])

    def test_normal_mode(self):
        self.assertIn("NORMAL MODE", build_system_prompt())

    def test_serious_mode(self):
        for flag in ("safety_critical", "financial", "security", "emergency"):
            with self.subTest(flag=flag):
                self.assertIn("SERIOUS MODE", build_system_prompt(ResponseContext(**{flag: True})))

    def test_privacy_and_truthfulness(self):
        prompt = build_system_prompt()
        self.assertIn("Never fabricate", prompt)
        self.assertIn("explicitly authorizes", prompt)

if __name__ == "__main__":
    unittest.main()
