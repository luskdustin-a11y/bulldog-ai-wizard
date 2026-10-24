"""Bounded, auditable diagnostics-to-repair controller.

Only explicitly registered, owner-approved repair functions may execute.
Never edits source code, installs packages, or deploys unreviewed changes.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class RepairResult:
    module: str
    before: str
    after: str
    attempted: bool
    verified: bool
    detail: str

def diagnose_and_repair(module, check, repair=None, *, owner_approved=False):
    """Check -> optional approved repair -> recheck; never mark blue on exception."""
    try:
        before = check()
        if before not in ("ok", "warning", "failed"):
            raise ValueError("invalid health result")
    except Exception as exc:
        return RepairResult(module, "failed", "failed", False, False, "health check error: " + type(exc).__name__)
    if before == "ok":
        return RepairResult(module, before, "ok", False, True, "initial check passed")
    if repair is None or not owner_approved:
        return RepairResult(module, before, before, False, False, "repair requires registered action and owner approval")
    try:
        repair()
        after = check()
        if after not in ("ok", "warning", "failed"):
            raise ValueError("invalid post-repair result")
    except Exception as exc:
        return RepairResult(module, before, "failed", True, False, "repair/recheck error: " + type(exc).__name__)
    return RepairResult(module, before, after, True, after == "ok", "post-repair check " + after)
