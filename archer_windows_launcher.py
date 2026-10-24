"""Bundled Windows entry point. Uses local files only; no installation side effects."""
import argparse
from archer_dashboard import ArcherDashboard
from archer_simulator import run_simulation
from archer_install_preflight import simulate_install
from archer_runtime_check import inspect_local_machine

def prepare_first_run_memory(database, backup_directory):
    """Initialize only a genuinely new database; never overwrite existing memory."""
    from pathlib import Path
    from archer_startup_recovery import startup_report
    from bulldawg_core import connect
    database = Path(database)
    report = startup_report(database, backup_directory)
    if report["database"]["state"] != "missing" or report["backups"]:
        return report
    if database.is_symlink() or database.exists():
        return report
    with connect() as connection:
        connection.execute("PRAGMA integrity_check").fetchone()
    return startup_report(database, backup_directory)

def memory_allows_launch(report):
    """Only launch when startup inspection explicitly approves the database."""
    return report.get("database", {}).get("safe_to_start") is True

def main():
    parser = argparse.ArgumentParser(description="ARCHER Windows desktop and simulator")
    parser.add_argument("--simulate", action="store_true", help="Run eight-department simulated events")
    parser.add_argument("--preflight", action="store_true", help="Review reported HP compatibility")
    parser.add_argument("--check-device", action="store_true", help="Read-only checks on this Windows machine")
    parser.add_argument("--thermal-sample", nargs=2, type=float, metavar=("CPU_C", "GPU_C"), help="Evaluate manually supplied CPU/GPU temperatures; no live hardware access")
    parser.add_argument("--health", action="store_true", help="Read-only local CPU RAM disk and process snapshot")
    parser.add_argument("--ai-status", action="store_true", help="Check local AI engine and model")
    args = parser.parse_args()
    if args.ai_status:
        import json
        from archer_model import local_model_status
        result = local_model_status()
        print(json.dumps(result, indent=2))
        return 0 if result["ready"] else 1
    if args.health:
        import json
        from archer_windows_health import snapshot
        print(json.dumps(snapshot(), indent=2))
        return 0
    if args.thermal_sample is not None:
        import json
        from archer_thermal_advisor import advise_cooling
        print(json.dumps(advise_cooling(*args.thermal_sample), indent=2))
        return 0
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
    import tkinter as tk
    from tkinter import simpledialog, messagebox
    from pathlib import Path
    from archer_pin import PinGate
    gate = PinGate(Path.home() / '.bulldawg_ai' / 'owner_pin.json')
    root = tk.Tk()
    root.withdraw()
    if not gate.configured():
        first = simpledialog.askstring('ARCHER setup', 'Choose your 4-digit PIN', show='*', parent=root)
        if first is None:
            root.destroy()
            return 1
        second = simpledialog.askstring('ARCHER setup', 'Confirm your 4-digit PIN', show='*', parent=root)
        if first != second:
            messagebox.showerror('ARCHER', 'PINs do not match', parent=root)
            root.destroy()
            return 1
        try:
            gate.setup(first)
        except (ValueError, PermissionError, OSError) as exc:
            messagebox.showerror('ARCHER', str(exc), parent=root)
            root.destroy()
            return 1
    else:
        for _ in range(5):
            supplied = simpledialog.askstring('ARCHER unlock', 'Enter your 4-digit PIN', show='*', parent=root)
            if supplied is None:
                root.destroy()
                return 1
            if gate.unlock(supplied):
                break
        if not gate.unlocked:
            messagebox.showerror('ARCHER', 'Access denied. Try again later.', parent=root)
            root.destroy()
            return 1
    from bulldawg_core import DB, ROOT
    report = prepare_first_run_memory(DB, ROOT / "backups")
    if not memory_allows_launch(report):
        messagebox.showerror("ARCHER memory protection", "Memory needs owner-reviewed recovery. No data has been overwritten.", parent=root)
        root.destroy()
        return 2
    root.destroy()
    ArcherDashboard().mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
