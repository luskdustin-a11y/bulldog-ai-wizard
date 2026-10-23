"""Connect R2 preventive checks to local, read-only runtime telemetry."""
from archer_preventive_maintenance import PreventiveMaintenance
from archer_windows_health import snapshot

def check_local_health(health=None):
    """Missing measurements are reported as unknown, never assumed healthy."""
    health = snapshot() if health is None else health
    total = health.get("disk_total_gb")
    free = health.get("disk_free_gb")
    metrics = {}
    if isinstance(total, (int, float)) and not isinstance(total, bool) and total > 0 and isinstance(free, (int, float)) and not isinstance(free, bool) and 0 <= free <= total:
        metrics["disk_free_pct"] = 100 * free / total
    ram = health.get("memory_percent")
    if isinstance(ram, (int, float)) and not isinstance(ram, bool):
        metrics["memory_used_pct"] = ram
    report = PreventiveMaintenance().inspect("supervisor", metrics)
    missing = sorted({"disk_free_pct", "memory_used_pct", "error_count", "backup_age_hours"} - metrics.keys())
    report["metrics_checked"] = metrics
    report["metrics_unavailable"] = missing
    report["status"] = "insufficient_data" if missing and not report["findings"] else report["status"]
    report["source"] = "local_health_snapshot" if health is not None else "unknown"
    return report
