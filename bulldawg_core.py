#!/usr/bin/env python3
"""Bulldawg AI local-first foundation. No network calls or package installs."""
import base64
import hashlib
import json
import os
import sqlite3
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / ".bulldawg_ai"
DB = ROOT / "core.db"
DEPARTMENTS = ("Shop AI", "VAL", "Hunting", "Property", "Hotshot", "Finances", "Stocks", "Supervisor")

VAULT_MAGIC = b"ARCHER-VAULT-1"
PREFIX = "enc1:"
ITERATIONS = 600_000
_key = None

def _vault_file():
    return ROOT / "vault.json"

def vault_enabled():
    return _vault_file().exists()

def _aes(key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise RuntimeError("Install cryptography to use the encrypted vault") from exc
    return AESGCM(key)

def _derive(passphrase, salt):
    if not isinstance(passphrase, str) or len(passphrase) < 12:
        raise ValueError("Passphrase must be at least 12 characters")
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, ITERATIONS, dklen=32)

def _encrypt(text):
    nonce = os.urandom(12)
    blob = _aes(_key).encrypt(nonce, text.encode(), VAULT_MAGIC)
    return PREFIX + base64.b64encode(nonce + blob).decode()

def _decrypt(value):
    if not value.startswith(PREFIX):
        return value
    raw = base64.b64decode(value[len(PREFIX):])
    return _aes(_key).decrypt(raw[:12], raw[12:], VAULT_MAGIC).decode()

def _require_unlocked():
    if vault_enabled() and _key is None:
        raise PermissionError("Vault is locked")

def lock_vault():
    global _key
    _key = None

def unlock_vault(passphrase):
    """Return True and hold the key in memory if the passphrase is correct."""
    global _key
    try:
        record = json.loads(_vault_file().read_text(encoding="utf-8"))
        key = _derive(passphrase, bytes.fromhex(record["salt"]))
        raw = base64.b64decode(record["check"])
        _aes(key).decrypt(raw[:12], raw[12:], VAULT_MAGIC)
    except (OSError, ValueError, KeyError, TypeError):
        return False
    except Exception as exc:
        if exc.__class__.__name__ == "InvalidTag":
            return False
        raise
    _key = key
    return True

def enable_vault(passphrase):
    """Create the vault and encrypt all existing plaintext notes."""
    global _key
    if vault_enabled():
        raise PermissionError("Vault already enabled")
    salt = os.urandom(16)
    key = _derive(passphrase, salt)
    nonce = os.urandom(12)
    check = base64.b64encode(nonce + _aes(key).encrypt(nonce, b"ok", VAULT_MAGIC)).decode()
    _key = key
    try:
        with managed_connection() as db:
            for note_id, text in db.execute("SELECT id,text FROM notes").fetchall():
                db.execute("UPDATE notes SET text=? WHERE id=?", (_encrypt(text), note_id))
            ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
            with _vault_file().open("x", encoding="utf-8") as stream:
                json.dump({"salt": salt.hex(), "check": check}, stream)
    except BaseException:
        _key = None
        raise
    if os.name != "nt":
        os.chmod(_vault_file(), 0o600)

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

@contextmanager
def managed_connection():
    """Commit/rollback and ALWAYS close SQLite handles (including on Windows)."""
    db = connect()
    try:
        with db:
            yield db
    finally:
        db.close()

def add_note(department, text):
    if department not in DEPARTMENTS:
        raise ValueError("Unknown department")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Empty note")
    if len(text) > 10000:
        raise ValueError("Note exceeds 10,000 characters")
    _require_unlocked()
    value = text.strip()
    if vault_enabled():
        value = _encrypt(value)
    with managed_connection() as db:
        db.execute("INSERT INTO notes(department,text,created) VALUES(?,?,?)",
                   (department, value, datetime.now(timezone.utc).isoformat()))

def list_notes(department=None):
    if department is not None and department not in DEPARTMENTS:
        raise ValueError("Unknown department")
    _require_unlocked()
    with managed_connection() as db:
        if department:
            rows = db.execute("SELECT id,department,text,created FROM notes WHERE department=? ORDER BY id DESC", (department,)).fetchall()
        else:
            rows = db.execute("SELECT id,department,text,created FROM notes ORDER BY id DESC").fetchall()
    notes = [dict(zip(("id","department","text","created"), row)) for row in rows]
    for note in notes:
        note["text"] = _decrypt(note["text"])
    return notes

def health():
    with managed_connection() as db:
        count = db.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    return {"status":"ok","mode":"offline","departments":list(DEPARTMENTS),"notes":count,
            "database":str(DB),"encrypted":vault_enabled(),"vault_locked":vault_enabled() and _key is None,"ai_model_connected":False,
            "phone_sync_enabled":False}

def main():
    import argparse
    p = argparse.ArgumentParser(description="Bulldawg AI offline core")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("health")
    sub.add_parser("enable-vault")
    sub.add_parser("departments")
    add = sub.add_parser("add-note")
    add.add_argument("department", choices=DEPARTMENTS)
    add.add_argument("text")
    ls = sub.add_parser("notes")
    ls.add_argument("--department", choices=DEPARTMENTS)
    args = p.parse_args()
    import getpass
    if args.command == "enable-vault":
        enable_vault(getpass.getpass("New vault passphrase (12+ chars): "))
        print(json.dumps({"vault_enabled": True}))
        return
    if vault_enabled() and args.command in ("add-note", "notes") and not unlock_vault(getpass.getpass("Vault passphrase: ")):
        sys.exit("Wrong passphrase")
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
