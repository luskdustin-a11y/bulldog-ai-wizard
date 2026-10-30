"""Integrated Windows acceptance inventory: fails closed on missing features."""
import importlib
import json
import subprocess
import sys
from pathlib import Path

def main():
    tests = {}
    def check(name, callback):
        try:
            tests[name] = {"passed": bool(callback())}
        except Exception as exc:
            tests[name] = {"passed": False, "error": type(exc).__name__ + ": " + str(exc)[:200]}
    check("offline_laptop_acceptance", lambda: subprocess.run([sys.executable, "archer_laptop_acceptance.py"], capture_output=True, timeout=120).returncode == 0)
    from archer_model import _local_url
    def remote_blocked():
        try:
            _local_url("https://external.example")
        except ValueError:
            return True
        return False
    check("ai_remote_access_blocked", remote_blocked)
    from archer_voice import speak
    check("voice_empty_input_safe", lambda: speak("") is False)
    check("live_database_encrypted", lambda: False)
    check("gui_end_to_end_automated", lambda: False)
    check("local_ai_model_installed_and_answering", lambda: False)
    check("supervisor_recovery_implemented", lambda: False)
    check("vehicle_adapter_live_diagnostics", lambda: False)
    check("hunting_camera_automatic_sync", lambda: False)
    check("business_live_integrations", lambda: False)
    check("android_apk_and_secure_sync", lambda: False)
    check("physical_hp_hardware_tested", lambda: False)
    report = {"passed": sum(v["passed"] for v in tests.values()), "total": len(tests), "checks": tests}
    Path("archer-integration-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] == report["total"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
