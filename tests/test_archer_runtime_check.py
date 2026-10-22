import unittest
from unittest.mock import patch
from archer_runtime_check import inspect_local_machine

class RuntimeCheckTests(unittest.TestCase):
    def test_read_only_report(self):
        with patch("archer_runtime_check.request.urlopen", side_effect=OSError("offline")):
            result = inspect_local_machine()
        self.assertTrue(result["device_scanned"])
        self.assertFalse(result["local_model_server"])
        self.assertFalse(result["owner_login_enabled"])
        self.assertFalse(result["database_encrypted"])
        self.assertGreaterEqual(result["free_disk_gb"], 0)
