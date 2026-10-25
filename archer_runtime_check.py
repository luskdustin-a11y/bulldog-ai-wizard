"""Read-only checks on the machine actually running ARCHER. No installation."""
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from archer_platform import http_response

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
        with http_response("http://127.0.0.1:11434/api/tags", timeout=2,
                           allowed_hosts={"127.0.0.1"}, allow_loopback_http=True) as response:
            raw = response.read(200_001)
        if len(raw) > 200_000:
            raise ValueError('Model catalog exceeds limit')
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get('models'), list):
            raise ValueError('Invalid model catalog')
        models = payload['models']
        if len(models) > 200 or any(not isinstance(m, dict)
                or not isinstance(m.get('name'), str) or not 0 < len(m['name']) <= 512
                for m in models):
            raise ValueError('Invalid model entries')
        names = [m['name'] for m in models]
        result["local_model_server"] = True
        result["model_names"] = names
    except (OSError, ValueError, KeyError, RecursionError):
        pass
    return result

if __name__ == "__main__":
    print(json.dumps(inspect_local_machine(), indent=2))
