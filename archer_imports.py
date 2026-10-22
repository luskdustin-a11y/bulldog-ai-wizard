"""Private, local-only import staging. No account logins, API requests or live hardware."""
import csv
import hashlib
import json
from pathlib import Path

CATEGORIES = ("diagnostics", "hunting", "property", "hotshot", "finances", "stocks")
ALLOWED = {
    "diagnostics": {".json", ".csv"},
    "hunting": {".jpg", ".jpeg", ".png", ".csv", ".json"},
    "property": {".csv", ".json"},
    "hotshot": {".csv", ".json"},
    "finances": {".csv", ".json"},
    "stocks": {".csv", ".json"},
}
MAX_SIZE = 25 * 1024 * 1024

def stage_file(category, source, destination_root):
    if category not in CATEGORIES:
        raise ValueError("Unknown department import category")
    source = Path(source).expanduser().resolve(strict=True)
    if not source.is_file() or source.is_symlink():
        raise ValueError("Only regular local files are accepted")
    if source.suffix.lower() not in ALLOWED[category]:
        raise ValueError("Unsupported file format")
    size = source.stat().st_size
    if not 0 < size <= MAX_SIZE:
        raise ValueError("File is empty or exceeds 25 MB")
    raw = source.read_bytes()
    suffix = source.suffix.lower()
    if suffix == ".json":
        json.loads(raw.decode("utf-8-sig"))
    elif suffix == ".csv":
        sample = raw.decode("utf-8-sig")
        if not list(csv.reader(sample.splitlines())):
            raise ValueError("Empty CSV")
    elif suffix in (".jpg", ".jpeg") and not raw.startswith(bytes.fromhex("ffd8ff")):
        raise ValueError("Invalid JPEG header")
    elif suffix == ".png" and not raw.startswith(bytes.fromhex("89504e470d0a1a0a")):
        raise ValueError("Invalid PNG header")
    digest = hashlib.sha256(raw).hexdigest()
    folder = Path(destination_root).expanduser().resolve() / category
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (digest + suffix)
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("Existing staged file differs")
    else:
        with target.open("xb") as out:
            out.write(raw)
    return {"category": category, "file": str(target), "sha256": digest, "bytes": size,
            "imported_into_live_system": False, "external_upload": False,
            "automated_analysis": False}
