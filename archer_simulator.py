"""ARCHER isolated laptop simulation: no real device, network or financial actions."""
import json
import tempfile
from pathlib import Path

SCENARIOS = {
    "Shop AI": {"input": "P1211 diagnostic trouble code", "expected": "simulated vehicle fault"},
    "VAL": {"input": "EGT temperature warning", "expected": "simulated truck telemetry"},
    "Hunting": {"input": "Deer spotted at six foot blind", "expected": "simulated camera event"},
    "Property": {"input": "Roof repair scheduled", "expected": "simulated property task"},
    "Hotshot": {"input": "Dispatch a trailer load", "expected": "simulated load request"},
    "Finances": {"input": "Reconcile an invoice", "expected": "simulated ledger event"},
    "Stocks": {"input": "Portfolio price changed", "expected": "simulated market event"},
    "Supervisor": {"input": "Storage service failed", "expected": "simulated failure event"},
}

def run_simulation(output_dir=None):
    """Exercise representative department events without touching real records."""
    from archer_brain import route
    events = []
    for department, scenario in SCENARIOS.items():
        detected = route(scenario["input"])
        events.append({
            "department": department,
            "input": scenario["input"],
            "expected_event": scenario["expected"],
            "detected_department": detected,
            "passed": detected == department,
            "simulated": True,
        })
    report = {
        "simulation_only": True,
        "real_hardware_connected": False,
        "external_accounts_connected": False,
        "events": events,
        "passed": sum(e["passed"] for e in events),
        "total": len(events),
    }
    if output_dir is not None:
        path = Path(output_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / "archer_simulation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

if __name__ == "__main__":
    print(json.dumps(run_simulation(), indent=2))
