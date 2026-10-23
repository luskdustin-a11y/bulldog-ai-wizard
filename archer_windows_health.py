"""Read-only Windows runtime health snapshot, no privileged operations.

No serial numbers, process command lines, environment variables or network traffic.
Temperature sensors require a separately approved hardware adapter.
"""
import os
import platform
import shutil
from pathlib import Path

def snapshot():
    disk = shutil.disk_usage(Path.home())
    report = {"system": platform.system(), "mode": "read_only",
              "disk_free_gb": round(disk.free / 1024**3, 2),
              "disk_total_gb": round(disk.total / 1024**3, 2),
              "cpu_percent": None, "memory_percent": None,
              "process_count": None, "temperatures_c": None,
              "limitations": []}
    try:
        import psutil
    except ImportError:
        report["limitations"].append("Install optional psutil for CPU, RAM and process usage.")
    else:
        report["cpu_percent"] = psutil.cpu_percent(interval=0.1)
        report["memory_percent"] = psutil.virtual_memory().percent
        report["process_count"] = len(psutil.pids())
        try:
            sensors = psutil.sensors_temperatures()
            if sensors:
                report["temperatures_c"] = {
                    key: [entry.current for entry in entries if entry.current is not None]
                    for key, entries in sensors.items()
                }
        except (AttributeError, OSError, NotImplementedError):
            pass
    if report["temperatures_c"] is None:
        report["limitations"].append("No verified temperature adapter; Windows sensor support varies.")
    return report
