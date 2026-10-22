#!/usr/bin/env python3
"""Bulldawg AI local-first foundation. No network calls or package installs."""
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".bulldawg_ai"
DB = ROOT / "core.db"
DEPARTMENTS = ("Shop AI", "VAL", "Hunting", "Property", "Hotshot", "Finances", "Stocks", "Supervisor")

def connect():
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != "nt":
        ROOT.chmod(0o700)
    db = sqlite3.connect(DB, timeout=15)
    db.execute("PRAGMA busy_timeout=15000")
    db.execute("PRAGMA journal_mode=DELETE")
    db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, department TEXT NOT NULL, text TEXT NOT NULL, created TEXT NOT NULL)")
    db.commit()
    if os.name != "nt":
        os.chmod(DB, 0o600)
    return db

def add_note(department, text):
    if department not in DEPARTMENTS:
        raise ValueError("Unknown department")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty note")
    if len(text) > 10000:
        raise ValueError("Note exceeds 10,000 characters")
    with connect() as db:
        db.execute("INSERT INTO notes(department,text,created) VALUES(?,?,?)",
                   (department, text.strip(), datetime.now(timezone.utc).isoformat()))

def list_notes(department=None):
    if department is not None and department not in DEPARTMENTS:
        raise ValueError("Unknown department")
    with connect() as db:
        if department:
            rows = db.execute("SELECT id,department,text,created FROM notes WHERE department=? ORDER BY id DESC", (department,)).fetchall()
        else:
            rows = db.execute("SELECT id,department,text,created FROM notes ORDER BY id DESC").fetchall()
    return [dict(zip(("id","department","text","created"), row)) for row in rows]

def health():
    with connect() as db:
        count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    return {"status":"ok","mode":"offline","departments":list(DEPARTMENTS),"notes":count,
            "database":str(DB),"encrypted":False,"ai_model_connected":False,
            "phone_sync_enabled":False}

def main():
    import argparse
    p = argparse.ArgumentParser(description="Bulldawg AI offline core")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("departments")
    add = sub.add_parser("add-note")
    add.add_argument("department", choices=DEPARTMENTS)
    add.add_argument("text")
    ls = sub.add_parser("notes")
    ls.add_argument("--department", choices=DEPARTMENTS)
    args = p.parse_args()
    if args.command == "health":
        result = health()
    elif args.command == "departments":
        result = list(DEPARTMENTS)
    elif args.command == "add-note":
        add_note(args.department, args.text)
        result = {"saved":True}
    else:
        result = list_notes(args.department)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
