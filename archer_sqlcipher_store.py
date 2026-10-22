"""Optional SQLCipher live notes storage. No automatic migration or plaintext fallback.

Requires separately installed sqlcipher3 binding and an explicit owner passphrase.
Never changes the existing core.db. The encrypted database is a separate file.
"""
from contextlib import contextmanager
from pathlib import Path
import os

def _driver():
    try:
        from sqlcipher3 import dbapi2 as sqlcipher
    except ImportError as exc:
        raise RuntimeError("SQLCipher Python binding is not installed") from exc
    return sqlcipher

def open_encrypted(path, passphrase):
    if not isinstance(passphrase, str) or len(passphrase) < 12:
        raise ValueError("Encrypted database requires a passphrase of at least 12 characters")
    path = Path(path).expanduser().resolve()
    if path.exists() and not path.is_file():
        raise ValueError("Database path is not a file")
    path.parent.mkdir(parents=True, exist_ok=True)
    db = _driver().connect(str(path), timeout=15)
    try:
        db.execute("PRAGMA key = '" + passphrase.replace("'", "''") + "'")
        db.execute("SELECT count(*) FROM sqlite_master").fetchone()
        db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, department TEXT NOT NULL, text TEXT NOT NULL, created TEXT NOT NULL)")
        db.commit()
        if os.name != "nt":
            os.chmod(path, 0o600)
        return db
    except BaseException:
        db.close()
        raise

def encrypted_health(path, passphrase):
    db = open_encrypted(path, passphrase)
    try:
        return {"encrypted": True, "notes": db.execute("SELECT COUNT(*) FROM notes").fetchone()[0], "database": str(Path(path).resolve())}
    finally:
        db.close()
