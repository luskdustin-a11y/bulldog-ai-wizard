"""RG coding department: propose isolated code changes, never deploy automatically."""
import ast
import difflib
import json
import re
from pathlib import Path
from archer_model import chat

MAX_FILE_BYTES = 12_000
MAX_OUTPUT = 120_000
BLOCKED = {".git", ".env", "secrets", "credentials", "__pycache__", "venv", ".venv"}
SYSTEM = """You are RG's coding assistant. Return ONLY a JSON object with keys
path, explanation, and code. code must be the complete replacement Python source.
Preserve existing interfaces. Do not include shell commands, markdown, or secrets.
Never claim tests ran or a change was deployed."""

class RepairRejected(ValueError):
    pass

def _safe_file(root, relative):
    root = Path(root).resolve()
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.suffix != ".py":
        raise RepairRejected("Only relative Python source paths are allowed")
    if any(part.lower() in BLOCKED or part.startswith(".") for part in path.parts):
        raise RepairRejected("Protected path")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root) or not resolved.is_file() or resolved.is_symlink():
        raise RepairRejected("File is missing, linked, or outside project")
    if resolved.stat().st_size > MAX_FILE_BYTES:
        raise RepairRejected("File too large")
    return resolved

def propose_repair(root, relative, problem, model="llama3.2"):
    """Return reviewable change; does not write or execute generated code."""
    if not isinstance(problem, str) or not problem.strip() or len(problem) > 4000:
        raise RepairRejected("Problem must contain 1-4000 characters")
    source_file = _safe_file(root, relative)
    original = source_file.read_text(encoding="utf-8")
    prompt = json.dumps({"path": relative, "problem": problem, "original_code": original})
    if len(prompt) > 20_000:
        raise RepairRejected("Source and instructions exceed local model input limit")
    response = chat(prompt, SYSTEM, model=model)
    if len(response) > MAX_OUTPUT:
        raise RepairRejected("Model response too large")
    try:
        result = json.loads(response)
    except json.JSONDecodeError as exc:
        raise RepairRejected("Model did not return valid JSON") from exc
    if not isinstance(result, dict) or result.get("path") != relative:
        raise RepairRejected("Unexpected target path")
    code = result.get("code")
    if not isinstance(code, str) or not code.strip() or len(code.encode("utf-8")) > MAX_FILE_BYTES:
        raise RepairRejected("Invalid replacement code")
    try:
        ast.parse(code, filename=relative)
    except SyntaxError as exc:
        raise RepairRejected("Generated Python failed syntax validation") from exc
    diff = "".join(difflib.unified_diff(original.splitlines(True), code.splitlines(True),
                                        fromfile="current/" + relative, tofile="proposed/" + relative))
    if not diff:
        raise RepairRejected("Model made no changes")
    return {"path": relative, "explanation": str(result.get("explanation", ""))[:4000],
            "diff": diff, "code": code, "status": "PROPOSED_ONLY",
            "tests_run": False, "owner_approval_required": True}
