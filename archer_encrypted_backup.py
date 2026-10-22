"""Encrypted, local-only backup using authenticated AES-GCM.
Requires separately installed cryptography. Never uploads or overwrites.
"""
import hashlib
import os
from pathlib import Path
from archer_backup import backup, verify
import tempfile

MAGIC = b"ARCHER-ENC-1"
ITERATIONS = 600000

def _aes():
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise RuntimeError("Install cryptography to use encrypted backups") from exc
    return AESGCM

def encrypt_backup(destination, passphrase):
    if not isinstance(passphrase, str) or len(passphrase) < 12:
        raise ValueError("Backup passphrase must be at least 12 characters")
    destination = Path(destination).expanduser().resolve()
    if destination.exists():
        raise FileExistsError("Refusing to overwrite encrypted backup")
    aes = _aes()
    with tempfile.TemporaryDirectory() as directory:
        plain = Path(directory) / "backup.db"
        backup(plain)
        raw = plain.read_bytes()
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, ITERATIONS, dklen=32)
    ciphertext = aes(key).encrypt(nonce, raw, MAGIC)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(MAGIC + salt + nonce + ciphertext)
    return {"encrypted": True, "file": str(destination)}

def decrypt_backup(source, destination, passphrase):
    aes = _aes()
    source = Path(source).expanduser().resolve()
    destination = Path(destination).expanduser().resolve()
    if destination.exists():
        raise FileExistsError("Refusing to overwrite restored database")
    data = source.read_bytes()
    if not data.startswith(MAGIC) or len(data) < len(MAGIC) + 16 + 12 + 16:
        raise ValueError("Invalid encrypted backup")
    offset = len(MAGIC)
    salt, nonce, ciphertext = data[offset:offset+16], data[offset+16:offset+28], data[offset+28:]
    key = hashlib.pbkdf2_hmac("sha256", passphrase.encode(), salt, ITERATIONS, dklen=32)
    raw = aes(key).decrypt(nonce, ciphertext, MAGIC)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(raw)
    try:
        report = verify(destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return report
