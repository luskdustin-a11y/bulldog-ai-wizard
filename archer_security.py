"""Local password verifier and export-safe redaction helpers.

No remote authentication. Passwords are not stored in plaintext.
"""
import hashlib
import hmac
import os
import secrets

ITERATIONS = 600_000

def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return "pbkdf2_sha256$%d$%s$%s" % (ITERATIONS, salt.hex(), digest.hex())

def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt, digest = encoded.split("$")
        if algorithm != "pbkdf2_sha256" or int(rounds) < 100_000:
            return False
        calculated = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(calculated, bytes.fromhex(digest))
    except (ValueError, TypeError, OverflowError):
        return False

def private_file(path):
    if os.name != "nt":
        os.chmod(path, 0o600)
