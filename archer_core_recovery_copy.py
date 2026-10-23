"""Archie protected recovery copy policy and offline verification.

A recovery bundle must be explicitly selected by the owner. This module only
checks a manifest against local files; it never copies, deletes or restores.
"""
import hashlib
from pathlib import Path

PROTECTED_CORE_FILES = frozenset({
    "bulldawg_core.py", "archer_owner_authority.py",
    "archer_intrusion_guard.py", "archer_protected_core_reset.py",
    "archer_security_baseline.py",
})

def verify_recovery_copy(directory, manifest):
    root = Path(directory).expanduser().resolve()
    if not isinstance(manifest, dict) or not PROTECTED_CORE_FILES <= manifest.keys():
        return {"verified": False, "reason": "Missing protected core manifest entries"}
    checked = []
    for filename, expected in sorted(manifest.items()):
        if filename not in PROTECTED_CORE_FILES:
            return {"verified": False, "reason": "Unexpected recovery file"}
        if not isinstance(expected, str) or len(expected) != 64:
            return {"verified": False, "reason": "Invalid checksum"}
        path = root / filename
        if not path.is_file() or path.is_symlink() or path.resolve().parent != root:
            return {"verified": False, "reason": "Missing or unsafe recovery file"}
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            return {"verified": False, "reason": "Recovery file integrity mismatch"}
        checked.append(filename)
    return {"verified": True, "files": checked, "read_only": True,
            "note": "Checksums detect corruption; authenticity requires signed trusted manifest"}
