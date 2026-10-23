"""ARCHER recovery coordinator: integrates existing local backup, verification and restore.
No automatic overwrites or cloud transfer.
"""
from pathlib import Path
import json
from datetime import datetime, timezone
from archer_backup import backup, verify, restore

def snapshot(directory):
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    name = "archer-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".sqlite3"
    target = directory / name
    result = backup(target)
    validation = verify(target)
    if result["sha256"] != validation["sha256"]:
        target.unlink(missing_ok=True)
        raise ValueError("Backup verification mismatch")
    return {"backup": result, "verification": validation}

def recover(source, destination, *, approve=False):
    if not approve:
        raise PermissionError("Recovery requires owner approval")
    validation = verify(source)
    restored = restore(source, destination, approve=True)
    final = verify(destination)
    if validation["sha256"] != final["sha256"]:
        Path(destination).unlink(missing_ok=True)
        raise ValueError("Restored database checksum mismatch")
    return {"restore": restored, "verified": final}

def status(path):
    try:
        return {"ready": True, "backup": verify(path)}
    except (OSError, ValueError) as exc:
        return {"ready": False, "reason": str(exc)}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("snapshot", "status", "recover"))
    parser.add_argument("source")
    parser.add_argument("destination", nargs="?")
    parser.add_argument("--approve", action="store_true")
    args = parser.parse_args()
    if args.action == "snapshot":
        output = snapshot(args.source)
    elif args.action == "status":
        output = status(args.source)
    else:
        if not args.destination:
            parser.error("recover requires destination")
        output = recover(args.source, args.destination, approve=args.approve)
    print(json.dumps(output, indent=2))
