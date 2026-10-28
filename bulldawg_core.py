#!/usr/bin/env python3
"""Bulldawg AI local-first foundation. No network calls or package installs."""
import base64
import hashlib
import json
import os
import shutil
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

def _backup_dir():
    return ROOT / "backups"

def backup_before_migration():
    """Consistent copy of the notes database, kept permanently. Returns its path."""
    _backup_dir().mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    target = _backup_dir() / f"core-pre-vault-{stamp}.db"
    source = connect()
    try:
        copy = sqlite3.connect(target)
        try:
            source.backup(copy)
        finally:
            copy.close()
    finally:
        source.close()
    if os.name != "nt":
        os.chmod(target, 0o600)
    return target

def restore_backup(backup_path):
    """Restore a pre-migration backup. Current DB is kept as .replaced, never deleted."""
    global _key
    backup_path = Path(backup_path)
    check = sqlite3.connect(backup_path)
    try:
        if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Backup failed integrity check")
        check.execute("SELECT COUNT(*) FROM notes").fetchone()
    finally:
        check.close()
    if DB.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        os.replace(DB, DB.with_name(f"{DB.name}.replaced-{stamp}"))
    shutil.copy2(backup_path, DB)
    if os.name != "nt":
        os.chmod(DB, 0o600)
    _vault_file().unlink(missing_ok=True)
    _key = None

def enable_vault(passphrase):
    """Encrypt all notes. A verified backup is taken first and any failure rolls back.

    The vault file is written first (readers pass plaintext rows through), and the
    conversion is one transaction, so a crash leaves every note readable.
    """
    global _key
    if vault_enabled():
        raise PermissionError("Vault already enabled")
    salt = os.urandom(16)
    key = _derive(passphrase, salt)
    nonce = os.urandom(12)
    check = base64.b64encode(nonce + _aes(key).encrypt(nonce, b"ok", VAULT_MAGIC)).decode()
    backup = backup_before_migration()
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    pending = _vault_file().with_suffix(".tmp")
    pending.write_text(json.dumps({"salt": salt.hex(), "check": check}), encoding="utf-8")
    if os.name != "nt":
        os.chmod(pending, 0o600)
    os.replace(pending, _vault_file())
    _key = key
    try:
        with managed_connection() as db:
            originals = db.execute("SELECT id,text FROM notes").fetchall()
            for note_id, text in originals:
                if text.startswith(PREFIX):
                    continue
                db.execute("UPDATE notes SET text=? WHERE id=?", (_encrypt(text), note_id))
            for note_id, text in originals:
                stored = db.execute("SELECT text FROM notes WHERE id=?", (note_id,)).fetchone()[0]
                if _decrypt(stored) != text:
                    raise RuntimeError("Verification failed for note %d" % note_id)
    except BaseException:
        _key = None
        _vault_file().unlink(missing_ok=True)
        raise
    return backup

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
        backup = enable_vault(getpass.getpass("New vault passphrase (12+ chars): "))
        print(json.dumps({"vault_enabled": True, "backup": str(backup)}))
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
