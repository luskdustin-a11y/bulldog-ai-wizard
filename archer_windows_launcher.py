"""Bundled Windows entry point. Uses local files only; no installation side effects."""
import argparse
from archer_dashboard import ArcherDashboard
from archer_simulator import run_simulation
from archer_install_preflight import simulate_install
from archer_runtime_check import inspect_local_machine

def main():
    parser = argparse.ArgumentParser(description="ARCHER Windows desktop and simulator")
    parser.add_argument("--simulate", action="store_true", help="Run eight-department simulated events")
    parser.add_argument("--preflight", action="store_true", help="Review reported HP compatibility")
    parser.add_argument("--check-device", action="store_true", help="Read-only checks on this Windows machine")
    args = parser.parse_args()
    if args.check_device:
        import json
        print(json.dumps(inspect_local_machine(), indent=2))
        return 0
    if args.simulate:
        import json
        result = run_simulation()
        print(json.dumps(result, indent=2))
        return 0 if result["passed"] == result["total"] else 1
    if args.preflight:
        import json
        print(json.dumps(simulate_install(), indent=2))
        return 0
    ArcherDashboard().mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
