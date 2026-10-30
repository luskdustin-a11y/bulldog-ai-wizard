"""Simulator functionality disabled pending verified behavioral tests.

The former eight-department routine only checked keyword routing and was
incorrectly used as evidence that departments worked. No simulated success
is reported until real, isolated behavior tests exist.
"""
import json
from pathlib import Path

def run_simulation(output_dir=None):
    report = {
        "simulation_only": True,
        "real_hardware_connected": False,
        "external_accounts_connected": False,
        "status": "NOT_VERIFIED",
        "reason": "Misleading keyword-routing checks removed; functional scenarios not implemented.",
        "events": [],
        "passed": 0,
        "total": 0,
        "verified_functional_tests": 0,
    }
    if output_dir is not None:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "archer_simulation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

if __name__ == "__main__":
    print(json.dumps(run_simulation(), indent=2))
