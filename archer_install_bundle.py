"""Fail-closed offline verification for a future complete ARCHER installation bundle.

This does NOT install software or authenticate the bundle publisher.
"""
import hashlib
import json
import zipfile
from pathlib import PurePosixPath

REQUIRED = frozenset({
    "archer_windows_launcher.py",
    "archer_brain.py",
    "archer_dashboard.py",
    "archer_model.py",
    "archer_voice.py",
    "archer_pin.py",
    "archer_security.py",
    "archer_backup.py",
    "archer_encrypted_backup.py",
    "archer_runtime_check.py",
    "archer_simulator.py",
})

def verify_bundle(path):
    """Return a machine-readable report; never extract or execute archive members."""
    errors = []
    checked = 0
    try:
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            names = [item.filename for item in entries if not item.is_dir()]
            if len(names) != len(set(names)):
                errors.append("Duplicate archive member names")
            for item in entries:
                name = item.filename
                p = PurePosixPath(name)
                if name.startswith("/") or "\\" in name or ".." in p.parts or not name or ":" in name:
                    errors.append("Unsafe archive path: " + name)
                if item.flag_bits & 1:
                    errors.append("Encrypted archive member: " + name)
                if item.file_size > 200 * 1024 * 1024:
                    errors.append("Oversized archive member: " + name)
            missing = REQUIRED.difference(names)
            if missing:
                errors.append("Missing required core files: " + ", ".join(sorted(missing)))
            if "bundle-manifest.json" not in names:
                errors.append("Missing bundle-manifest.json")
            if errors:
                return {"passed": False, "checked": checked, "errors": errors}
            with archive.open("bundle-manifest.json") as f:
                manifest = json.loads(f.read(1024 * 1024 + 1))
            hashes = manifest.get("sha256", {})
            if not isinstance(hashes, dict) or set(hashes) != set(names) - {"bundle-manifest.json"}:
                errors.append("Manifest must enumerate every payload file exactly once")
            else:
                for name in sorted(hashes):
                    expected = hashes[name]
                    if not isinstance(expected, str) or len(expected) != 64:
                        errors.append("Invalid SHA256 for " + name)
                        continue
                    digest = hashlib.sha256()
                    with archive.open(name) as f:
                        while chunk := f.read(1024 * 1024):
                            digest.update(chunk)
                    checked += 1
                    if digest.hexdigest() != expected.lower():
                        errors.append("SHA256 mismatch: " + name)
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError, KeyError, ValueError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc)[:160])
    return {"passed": not errors, "checked": checked, "errors": errors}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    args = parser.parse_args()
    result = verify_bundle(args.bundle)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
