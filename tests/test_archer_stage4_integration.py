"""Stage 4: exercise real ARCHER entrypoint without changing a laptop."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import archer_windows_launcher
from archer_pin import PinGate


class LocalAISecurityTests(unittest.TestCase):
    def test_external_hosts_rejected(self):
        from archer_model import _local_url
        for url in ("https://example.com", "http://example.com", "http://127.0.0.1.evil.test:11434", "http://user:pass@localhost:11434"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                _local_url(url)

    def test_redirects_disabled_and_proxy_disabled(self):
        from urllib import request
        from archer_model import _LOCAL_OPENER, _NoRedirect
        self.assertTrue(any(isinstance(handler, _NoRedirect) for handler in _LOCAL_OPENER.handlers))
        proxies = [handler for handler in _LOCAL_OPENER.handlers if isinstance(handler, request.ProxyHandler)]
        self.assertEqual(len(proxies), 1)
        self.assertEqual(proxies[0].proxies, {})
        handler = _NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "https://example.com"))

class WindowsLauncherIntegrationTests(unittest.TestCase):
    def test_ai_status_reports_missing_model_without_launching_gui(self):
        with patch("archer_model.local_model_status", return_value={"ready": False, "server_running": False, "model_installed": False, "model": "llama3.2"}):
            status, report = self.invoke("--ai-status")
        self.assertEqual(status, 1)
        self.assertFalse(report["ready"])

    def test_ai_status_reports_missing_model(self):
        with patch("archer_model.local_model_status", return_value={"ready": False, "server_running": False, "model_installed": False, "model": "llama3.2"}):
            status, report = self.invoke("--ai-status")
        self.assertEqual(status, 1)
        self.assertFalse(report["ready"])

    def test_first_run_initializes_new_database_without_overwriting_existing(self):
        import bulldawg_core as core
        from archer_startup_recovery import startup_report
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "core.db"
            with patch.object(core, "ROOT", root), patch.object(core, "DB", db):
                report = archer_windows_launcher.prepare_first_run_memory(db, root / "backups")
                self.assertTrue(report["database"]["safe_to_start"])
                self.assertTrue(db.exists())
                db.write_bytes(b"not a database")
                damaged = archer_windows_launcher.prepare_first_run_memory(db, root / "backups")
                self.assertFalse(damaged["database"]["safe_to_start"])
                self.assertEqual(db.read_bytes(), b"not a database")

    def test_memory_gate_fails_closed(self):
        allowed = archer_windows_launcher.memory_allows_launch
        self.assertFalse(allowed({}))
        self.assertFalse(allowed({"database": {"state": "missing", "safe_to_start": False}}))
        self.assertFalse(allowed({"database": {"state": "damaged", "safe_to_start": False}}))
        self.assertTrue(allowed({"database": {"state": "healthy", "safe_to_start": True}}))

    def invoke(self, flag):
        stream = io.StringIO()
        with patch("sys.argv", ["ARCHER.exe", flag]), contextlib.redirect_stdout(stream):
            status = archer_windows_launcher.main()
        return status, json.loads(stream.getvalue())

    def test_preflight_is_honest_about_incomplete_install(self):
        status, report = self.invoke("--preflight")
        self.assertEqual(status, 0)
        self.assertTrue(report["simulation_only"])
        self.assertFalse(report["ready_to_install_complete_system"])
        self.assertEqual(report["laptop"]["ram_gb"], 64)

    def test_simulated_departments(self):
        status, report = self.invoke("--simulate")
        self.assertEqual(status, 0, report)
        self.assertEqual(report["total"], 8)
        self.assertEqual(report["passed"], 8)
        self.assertFalse(report["real_hardware_connected"])

    def test_device_check_is_read_only(self):
        sample = {"device_scanned": True, "free_disk_gb": 100}
        with patch("archer_windows_launcher.inspect_local_machine", return_value=sample):
            status, report = self.invoke("--check-device")
        self.assertEqual(status, 0)
        self.assertEqual(report, sample)


class OwnerPinSecurityTests(unittest.TestCase):
    def test_pin_never_stored_plaintext_and_lockout(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "owner_pin.json"
            gate = PinGate(path)
            gate.setup("9876")
            self.assertNotIn("9876", path.read_text(encoding="utf-8"))
            gate.lock()
            self.assertFalse(gate.unlock("1111"))
            self.assertTrue(gate.unlock("9876"))
            gate.lock()
            for _ in range(5):
                self.assertFalse(gate.unlock("1111"))
            self.assertFalse(gate.unlock("9876"))
            self.assertTrue(path.with_suffix(".lock").exists())

    def test_reject_non_four_digit_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            gate = PinGate(Path(tmp) / "owner_pin.json")
            for bad in ("123", "12345", "abcd", "１２３４"):
                with self.subTest(pin=bad):
                    with self.assertRaises(ValueError):
                        gate.setup(bad)


if __name__ == "__main__":
    unittest.main()
