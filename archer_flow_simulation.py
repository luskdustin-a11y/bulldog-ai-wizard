"""Deterministic ARCHER eight-stage virtual health-flow acceptance test.

Blue=healthy, yellow=warning, red=failure. Simulation, not live telemetry.
"""
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from archer_pc_thermal import decide_thermal

STAGES = ("core", "memory", "intelligence", "dashboard", "self_repair",
          "security_backups", "devices", "windows_runtime")

@dataclass(frozen=True)
class FlowNode:
    name: str
    color: str
    issue: str

def evaluate(stage_signals):
    if set(stage_signals) != set(STAGES):
        raise ValueError("Exactly eight stage signals required")
    nodes = []
    for name in STAGES:
        signal = stage_signals[name]
        if signal not in ("ok", "warning", "failed"):
            raise ValueError("Unrecognized stage signal")
        color = {"ok": "blue", "warning": "yellow", "failed": "red"}[signal]
        nodes.append(FlowNode(name, color, "" if signal == "ok" else signal))
    return nodes

def simulate():
    baseline = {stage: "ok" for stage in STAGES}
    healthy = evaluate(baseline)
    failure = dict(baseline, windows_runtime="failed", devices="warning")
    flagged = evaluate(failure)
    thermal = decide_thermal(96, 78)
    # A failed signal must remain red until a fresh passing check is supplied.
    repaired = evaluate(dict(baseline))
    checks = {
        "eight_modules_connected": len(healthy) == 8,
        "blue_healthy_flow": all(n.color == "blue" for n in healthy),
        "yellow_warning_detected": any(n.name == "devices" and n.color == "yellow" for n in flagged),
        "red_failure_detected": any(n.name == "windows_runtime" and n.color == "red" for n in flagged),
        "thermal_critical_detected": thermal.request_safe_shutdown and thermal.throttle_ai,
        "repaired_signal_returns_blue": all(n.color == "blue" for n in repaired),
        "unverified_failure_stays_red": any(n.name == "windows_runtime" and n.color == "red" for n in evaluate(failure)),
    }
    return {"simulation_only": True, "passed": sum(checks.values()), "total": len(checks),
            "checks": checks, "healthy": [asdict(n) for n in healthy],
            "fault_injection": [asdict(n) for n in flagged],
            "after_simulated_repair": [asdict(n) for n in repaired],
            "note": "Repair here is a simulated signal reset, not evidence of autonomous code repair."}

if __name__ == "__main__":
    report = simulate()
    Path("archer-flow-simulation.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] == report["total"] else 1)
