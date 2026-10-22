"""Local-only ARCHER backup and restore. Never uploads data or overwrites without approval."""
import argparse
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
import bulldawg_core as core

def checksum(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def backup(destination):
    target = Path(destination).expanduser().resolve()
    if target.exists():
        raise FileExistsError("Backup destination exists; refusing overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    with core.managed_connection() as source:
        with closing(sqlite3.connect(target)) as output:
            source.backup(output)
    return {"file": str(target), "sha256": checksum(target), "encrypted": False}

def verify(path):
    target = Path(path).expanduser().resolve()
    if not target.is_file():
        raise FileNotFoundError(target)
    with closing(sqlite3.connect(f"file:{target.as_posix()}?mode=ro", uri=True)) as db:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if integrity != "ok" or "notes" not in names:
            raise ValueError("Backup integrity or schema invalid")
        count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    return {"valid": True, "notes": count, "sha256": checksum(target)}

def restore(source, destination, approve=False):
    if not approve:
        raise PermissionError("Explicit restore approval required")
    verified = verify(source)
    target = Path(destination).expanduser().resolve()
    if target.exists():
        raise FileExistsError("Refusing to overwrite an existing database")
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(f"file:{Path(source).expanduser().resolve().as_posix()}?mode=ro", uri=True)) as original:
        with closing(sqlite3.connect(target)) as output:
            original.backup(output)
    return {"restored": True, "notes": verified["notes"], "destination": str(target)}

def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("backup").add_argument("destination")
    commands.add_parser("verify").add_argument("source")
    restore_cmd = commands.add_parser("restore")
    restore_cmd.add_argument("source")
    restore_cmd.add_argument("destination")
    restore_cmd.add_argument("--approve", action="store_true")
    args = parser.parse_args()
    if args.action == "backup":
        result = backup(args.destination)
    elif args.action == "verify":
        result = verify(args.source)
    else:
        result = restore(args.source, args.destination, args.approve)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
