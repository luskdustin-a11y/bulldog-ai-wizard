"""Unverified simulator checks disabled; original preserved in Git history."""
import json
from pathlib import Path

def run():
    report = {"status": "NOT_VERIFIED", "passed": 0, "total": 0, "checks": {}}
    Path("archer-isolated-report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 1

if __name__ == "__main__":
    raise SystemExit(run())
