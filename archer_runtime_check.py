"""Read-only checks on the machine actually running ARCHER. No installation."""
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from urllib import request

def inspect_local_machine():
    home = Path.home()
    disk = shutil.disk_usage(home)
    result = {
        "device_scanned": True,
        "os": platform.platform(),
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
        "free_disk_gb": round(disk.free / (1024 ** 3), 2),
        "tkinter_available": False,
        "local_model_server": False,
        "model_names": [],
        "microphone_verified": False,
        "owner_login_enabled": False,
        "database_encrypted": False,
    }
    try:
        import tkinter
        result["tkinter_available"] = True
    except ImportError:
        pass
    try:
        with request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as response:
            payload = json.loads(response.read(200_000))
        result["local_model_server"] = True
        result["model_names"] = [str(m.get("name", "")) for m in payload.get("models", [])]
    except (OSError, ValueError, KeyError):
        pass
    return result

if __name__ == "__main__":
    print(json.dumps(inspect_local_machine(), indent=2))
