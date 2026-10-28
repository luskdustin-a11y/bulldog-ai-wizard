import json
import subprocess
import sys
import unittest
from archer_windows_health import snapshot

class WindowsHealthTests(unittest.TestCase):
    def test_snapshot_safe_schema(self):
        result = snapshot()
        self.assertEqual(result["mode"], "read_only")
        self.assertGreaterEqual(result["disk_free_gb"], 0)
        self.assertIn("temperatures_c", result)
        self.assertIn("limitations", result)

    def test_launcher_health_command(self):
        proc = subprocess.run([sys.executable, "archer_windows_launcher.py", "--health"],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["mode"], "read_only")
        self.assertIn("memory_percent", result)

if __name__ == "__main__":
    unittest.main()
