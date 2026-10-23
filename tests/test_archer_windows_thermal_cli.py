import json
import subprocess
import sys
import unittest

class WindowsLauncherThermalTests(unittest.TestCase):
    def run_sample(self, cpu, gpu):
        proc = subprocess.run([sys.executable, "archer_windows_launcher.py",
                               "--thermal-sample", str(cpu), str(gpu)],
                              capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_normal_sample_through_launcher(self):
        data = self.run_sample(45, 50)
        self.assertEqual(data["state"], "normal")
        self.assertEqual(data["control_mode"], "advisory_only")

    def test_critical_sample_through_launcher(self):
        data = self.run_sample(96, 80)
        self.assertTrue(data["request_safe_shutdown"])
        self.assertTrue(data["throttle_ai"])

if __name__ == "__main__":
    unittest.main()
