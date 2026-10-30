"""Headless simulated laptop acceptance test: no owner hardware touched."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from archer_pin import PinGate
from archer_simulator import run_simulation
from archer_install_preflight import simulate_install

def main():
    checks = {}
    hp = simulate_install()
    checks["hp_simulation_only"] = hp.get("simulation_only") is True and hp.get("device_scanned") is False
    result = run_simulation()
    checks["simulator_not_falsely_certified"] = result.get("status") == "NOT_VERIFIED" and result.get("verified_functional_tests") == 0
    with tempfile.TemporaryDirectory() as folder:
        pinfile = Path(folder) / "owner_pin.json"
        gate = PinGate(pinfile)
        gate.setup("4826")
        gate.lock()
        checks["correct_pin"] = gate.unlock("4826")
        gate.lock()
        checks["incorrect_pin"] = not gate.unlock("1111")
        for _ in range(4):
            gate.unlock("1111")
        gate2 = PinGate(pinfile)
        checks["restart_lockout"] = not gate2.unlock("4826")
        checks["pin_not_plaintext"] = "4826" not in pinfile.read_text()
    report = {"passed": sum(checks.values()), "total": len(checks), "checks": checks}
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] == report["total"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
