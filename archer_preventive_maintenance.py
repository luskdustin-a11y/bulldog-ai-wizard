"""R2 preventive-maintenance evaluator: offline, read-only, no autonomous code changes."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

@dataclass(frozen=True)
class Finding:
    component: str
    severity: str
    reason: str
    recommended_action: str
    automatic_repair_allowed: bool = False

class PreventiveMaintenance:
    """Deterministic rules; readings are observations, not proof of future failure."""
    def __init__(self, thresholds=None):
        self.thresholds = dict(thresholds or {"disk_free_pct": 10, "memory_used_pct": 90,
                                               "error_count": 5, "backup_age_hours": 48})
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0 for v in self.thresholds.values()):
            raise ValueError("Invalid thresholds")

    def inspect(self, component: str, metrics: Mapping):
        if not isinstance(component, str) or not component.strip() or not isinstance(metrics, Mapping):
            raise ValueError("Invalid component or metrics")
        findings = []
        rules = (
            ("disk_free_pct", "below", "warning", "Low free disk space", "Review storage and free space"),
            ("memory_used_pct", "above", "warning", "High memory utilization", "Investigate memory use"),
            ("error_count", "above", "warning", "Repeated errors", "Inspect error logs and isolate failing module"),
            ("backup_age_hours", "above", "warning", "Backup may be stale", "Create and verify an encrypted backup"),
        )
        for key, direction, severity, reason, action in rules:
            if key not in metrics:
                continue
            value = metrics[key]
            if not isinstance(value, (int, float)) or isinstance(value, bool) or value != value or value in (float("inf"), float("-inf")) or value < 0:
                raise ValueError("Invalid metric: " + key)
            if key.endswith("_pct") and value > 100:
                raise ValueError("Percentage exceeds 100")
            limit = self.thresholds[key]
            triggered = value < limit if direction == "below" else value > limit
            if triggered:
                findings.append(Finding(component, severity, reason, action))
        return {"component": component, "checked_at": datetime.now(timezone.utc).isoformat(),
                "status": "attention" if findings else "no_thresholds_triggered",
                "findings": [item.__dict__ for item in findings],
                "read_only": True, "predicted_failure_guaranteed": False}
