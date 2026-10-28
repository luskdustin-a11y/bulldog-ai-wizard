"""R2 offline supervisor: health, backup checks, bounded verified recovery.

No code rewriting, network, privilege escalation, or automatic data restoration.
"""
from datetime import datetime, timezone
from pathlib import Path
from archer_r2_health_monitor import check_local_health
from archer_startup_recovery import inspect_backups

class R2Supervisor:
    def __init__(self, *, max_retries=1):
        if type(max_retries) is not int or not 0 <= max_retries <= 3:
            raise ValueError("Retry limit must be 0 through 3")
        self.max_retries = max_retries
        self._halted = False

    def emergency_stop(self):
        """Latch supervisor shutdown; no in-process API to clear it."""
        self._halted = True

    @property
    def halted(self):
        return self._halted

    def assess(self, health=None, backup_directory=None, error_count=None):
        report = check_local_health(health)
        metrics = dict(report["metrics_checked"])
        if error_count is not None:
            if type(error_count) is not int or error_count < 0:
                raise ValueError("Invalid error count")
            metrics["error_count"] = error_count
        backup_status = "not_checked"
        if backup_directory is not None:
            directory = Path(backup_directory)
            verified = [item for item in inspect_backups(directory) if item["valid"]]
            if verified:
                newest = max(Path(item["file"]).stat().st_mtime for item in verified)
                metrics["backup_age_hours"] = max(0, (datetime.now(timezone.utc).timestamp() - newest) / 3600)
                backup_status = "verified"
            else:
                backup_status = "no_verified_backup"
        from archer_preventive_maintenance import PreventiveMaintenance
        result = PreventiveMaintenance().inspect("supervisor", metrics)
        result["metrics_checked"] = metrics
        result["metrics_unavailable"] = sorted({"disk_free_pct", "memory_used_pct", "error_count", "backup_age_hours"} - metrics.keys())
        result["backup_status"] = backup_status
        if backup_status == "no_verified_backup":
            result["findings"].append({"component": "supervisor", "severity": "warning",
                "reason": "No verified backup available", "recommended_action": "Create and verify an encrypted backup",
                "automatic_repair_allowed": False})
        if result["findings"]:
            result["status"] = "attention"
        elif result["metrics_unavailable"]:
            result["status"] = "insufficient_data"
        return result

    def recover_transient(self, operation, verify, *, approved=False):
        """Only owner-approved, idempotent callbacks; stop on unverified results."""
        if self._halted:
            raise PermissionError("R2 emergency stop is latched")
        if not approved:
            raise PermissionError("Recovery action requires owner approval")
        if not callable(operation) or not callable(verify):
            raise TypeError("Recovery and verification must be callable")
        errors = []
        for attempt in range(self.max_retries + 1):
            if self._halted:
                return {"recovered": False, "attempts": attempt,
                        "safe_mode_required": True, "errors": ["Emergency stop"]}
            try:
                operation()
                if self._halted:
                    return {"recovered": False, "attempts": attempt + 1,
                            "safe_mode_required": True, "errors": ["Emergency stop"]}
                if verify() is True and not self._halted:
                    return {"recovered": True, "attempts": attempt + 1}
                errors.append("Verification did not pass")
            except Exception as exc:
                errors.append(type(exc).__name__)
        return {"recovered": False, "attempts": self.max_retries + 1,
                "safe_mode_required": True, "errors": errors}
