"""Owner-only PIN gate for ARCHER. PIN is never saved in plaintext."""
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

ROUNDS = 300000
LIMIT = 5
LOCK_SECONDS = 300

class PinGate:
    def __init__(self, path):
        self.path = Path(path)
        self.failed = 0
        self.lock_until = 0.0
        self.unlocked = False

    def configured(self):
        return self.path.exists()

    def setup(self, pin):
        if self.configured():
            raise PermissionError("PIN already configured")
        if not isinstance(pin, str) or len(pin) != 4 or not pin.isascii() or not pin.isdecimal():
            raise ValueError("PIN must contain exactly four digits")
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, ROUNDS)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("x", encoding="utf-8") as stream:
            json.dump({"salt": salt.hex(), "digest": digest.hex()}, stream)
        if os.name != "nt":
            self.path.chmod(0o600)
        self.unlocked = True

    def unlock(self, pin):
        if time.monotonic() < self.lock_until:
            return False
        if not self.configured():
            return False
        try:
            record = json.loads(self.path.read_text(encoding="utf-8"))
            salt = bytes.fromhex(record["salt"])
            expected = bytes.fromhex(record["digest"])
            valid_format = isinstance(pin, str) and len(pin) == 4 and pin.isascii() and pin.isdecimal()
            supplied = pin.encode() if valid_format else b"invalid"
            actual = hashlib.pbkdf2_hmac("sha256", supplied, salt, ROUNDS)
            valid = valid_format and hmac.compare_digest(actual, expected)
        except (OSError, ValueError, KeyError, TypeError):
            valid = False
        if valid:
            self.failed = 0
            self.unlocked = True
            return True
        self.unlocked = False
        self.failed += 1
        if self.failed >= LIMIT:
            self.failed = 0
            self.lock_until = time.monotonic() + LOCK_SECONDS
        return False

    def lock(self):
        self.unlocked = False
