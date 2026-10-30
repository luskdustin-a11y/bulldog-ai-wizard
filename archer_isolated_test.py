"""Separate-process Windows component checks; never installs software or accesses devices."""
import json
import subprocess
import sys
from pathlib import Path

def run():
    checks = {}
    for name, flags in (("preflight", ["--preflight"]),):
        try:
            result = subprocess.run([sys.executable, "archer_windows_launcher.py", *flags], cwd=Path(__file__).parent, capture_output=True, text=True, timeout=60)
            checks[name] = {"passed": result.returncode == 0, "error": result.stderr[-300:] if result.returncode else ""}
        except subprocess.TimeoutExpired:
            checks[name] = {"passed": False, "error": "timeout"}
    report = {"passed": sum(item["passed"] for item in checks.values()), "total": len(checks), "checks": checks}
    Path("archer-isolated-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] == report["total"] else 1

if __name__ == "__main__":
    raise SystemExit(run())
