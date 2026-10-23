"""ARCHER startup recovery health gate (34% milestone candidate).

Read-only startup inspection. Never restores, deletes or uploads user data.
"""
from pathlib import Path
import json
import sqlite3
from archer_backup import verify

def inspect_database(database):
    path = Path(database).expanduser().resolve()
    if not path.exists():
        return {"state": "missing", "safe_to_start": False}
    try:
        with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            schema = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if integrity != "ok" or "notes" not in schema:
                return {"state": "damaged", "safe_to_start": False}
            count = connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        return {"state": "healthy", "safe_to_start": True, "notes": count}
    except (sqlite3.DatabaseError, OSError, ValueError):
        return {"state": "damaged", "safe_to_start": False}

def inspect_backups(directory):
    root = Path(directory).expanduser().resolve()
    results = []
    if not root.is_dir():
        return results
    for path in sorted(root.glob("archer-*.sqlite3"), reverse=True):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            report = verify(path)
            results.append({"file": str(path), "valid": True, "notes": report["notes"]})
        except (sqlite3.DatabaseError, OSError, ValueError):
            results.append({"file": str(path), "valid": False})
    return results

def startup_report(database, backup_directory):
    current = inspect_database(database)
    backups = inspect_backups(backup_directory)
    return {"database": current, "backups": backups,
            "recovery_available": any(item["valid"] for item in backups),
            "automatic_restore": False,
            "action": "continue" if current["safe_to_start"] else "require_owner_review"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("database")
    parser.add_argument("backup_directory")
    args = parser.parse_args()
    print(json.dumps(startup_report(args.database, args.backup_directory), indent=2))
