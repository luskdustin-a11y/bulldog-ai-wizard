"""Owner-approved, local-only staging and rollback for RG code proposals."""
import hashlib
import json
import os
from pathlib import Path
from rg_coding_department import _safe_file, RepairRejected

def stage_repair(root, proposal, approval, backup_dir):
    """Stage approved source in a separate directory; never touch live source."""
    if approval != "OWNER_APPROVED":
        raise RepairRejected("Explicit owner approval required")
    relative = proposal.get("path")
    source = _safe_file(root, relative)
    code = proposal.get("code")
    if not isinstance(code, str) or not code.strip():
        raise RepairRejected("Missing replacement")
    import ast
    ast.parse(code)
    original = source.read_bytes()
    base = Path(backup_dir).resolve()
    project = Path(root).resolve()
    if base == project or base.is_relative_to(project):
        raise RepairRejected("Backup/staging directory must be outside project")
    base.mkdir(parents=True, exist_ok=True)
    identity = hashlib.sha256((str(project) + ":" + relative).encode()).hexdigest()
    target = base / identity
    target.mkdir(exist_ok=True)
    (target / "original.py").write_bytes(original)
    (target / "proposed.py").write_text(code, encoding="utf-8")
    manifest = {"path": relative, "original_sha256": hashlib.sha256(original).hexdigest(),
                "proposed_sha256": hashlib.sha256(code.encode()).hexdigest(),
                "state": "STAGED_NOT_DEPLOYED"}
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest

def verify_staged(root, relative, backup_dir):
    """Check that the live source has not changed since staging."""
    source = _safe_file(root, relative)
    identity = hashlib.sha256((str(Path(root).resolve()) + ":" + relative).encode()).hexdigest()
    target = Path(backup_dir).resolve() / identity
    manifest = json.loads((target / "manifest.json").read_text())
    if manifest["path"] != relative:
        raise RepairRejected("Manifest target mismatch")
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["original_sha256"]:
        raise RepairRejected("Live source changed since staging")
    if hashlib.sha256((target / "proposed.py").read_bytes()).hexdigest() != manifest["proposed_sha256"]:
        raise RepairRejected("Staged proposal changed")
    return True
