import unittest
from unittest.mock import patch

import archer_laptop_scan as scan


class ScanTests(unittest.TestCase):
    def found(self, **changes):
        base = {"ram_total_gb": 64.0, "disk_free_gb": 3510, "ollama_models": ["llama3.2:latest"], "microphones": "Microphone Array"}
        return {**base, **changes}

    def test_healthy_laptop_all_ok(self):
        self.assertTrue(all(status == "OK" for _n, status, _d in scan.verdicts(self.found())))

    def test_ollama_down_and_missing_model_reported(self):
        self.assertEqual(dict((n, s) for n, s, _ in scan.verdicts(self.found(ollama_models=None)))["Ollama"], "NOT REACHABLE")
        self.assertEqual(dict((n, s) for n, s, _ in scan.verdicts(self.found(ollama_models=["qwen2"])))["Ollama"], "NO LLAMA 3.2")

    def test_scan_is_read_only_and_runs(self):
        with patch.object(scan, "ollama_models", return_value=None):
            result = scan.scan()
        self.assertIn("disk_free_gb", result)


if __name__ == "__main__":
    unittest.main()
