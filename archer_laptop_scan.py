"""Read-only scan of THIS computer. Writes a report file locally; nothing is uploaded or changed.

Only reads hardware/OS facts and asks the local Ollama (127.0.0.1) which models are installed.
"""
import ctypes
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from archer_install_preflight import REPORTED_HP


def powershell(command):
    if os.name != "nt":
        return ""
    try:
        done = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                              capture_output=True, text=True, timeout=30)
        return done.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def ram_gb():
    if os.name != "nt":
        return None

    class Status(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                    ("avail", ctypes.c_ulonglong), ("tpf", ctypes.c_ulonglong), ("apf", ctypes.c_ulonglong),
                    ("tv", ctypes.c_ulonglong), ("av", ctypes.c_ulonglong), ("ext", ctypes.c_ulonglong)]
    status = Status()
    status.length = ctypes.sizeof(Status)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    return round(status.total / 2**30, 1), round(status.avail / 2**30, 1)


def ollama_models():
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as reply:
            return [m.get("name") for m in json.load(reply).get("models", [])]
    except (OSError, ValueError):
        return None


def scan():
    drive = Path(os.environ.get("SystemDrive", "C:") + "\\") if os.name == "nt" else Path("/")
    usage = shutil.disk_usage(drive)
    ram = ram_gb()
    return {
        "windows": powershell("(Get-CimInstance Win32_OperatingSystem | ForEach-Object { $_.Caption + ' build ' + $_.BuildNumber })") or platform.platform(),
        "architecture": platform.machine(),
        "computer": powershell("(Get-CimInstance Win32_ComputerSystem | ForEach-Object { $_.Manufacturer + ' ' + $_.Model })"),
        "cpu": powershell("(Get-CimInstance Win32_Processor | ForEach-Object { $_.Name + ' (' + $_.NumberOfCores + ' cores, ' + $_.NumberOfLogicalProcessors + ' threads)' })"),
        "ram_total_gb": ram[0] if ram else None,
        "ram_available_gb": ram[1] if ram else None,
        "disk_total_gb": round(usage.total / 1e9),
        "disk_free_gb": round(usage.free / 1e9),
        "gpu": powershell("(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name + ' (' + [math]::Round($_.AdapterRAM/1MB) + ' MB reported)' }) -join '; '"),
        "microphones": powershell("(Get-PnpDevice -Class AudioEndpoint -Status OK | Where-Object { $_.FriendlyName -match 'Microphone|Mic' } | ForEach-Object { $_.FriendlyName }) -join '; '"),
        "ollama_models": ollama_models(),
        "archie_data_folder_exists": (Path(os.environ.get("LOCALAPPDATA", "")) / "BulldawgAI").is_dir(),
    }


def verdicts(found, reported=REPORTED_HP):
    notes = []
    if found["ram_total_gb"] is not None:
        notes.append(("RAM", "OK" if found["ram_total_gb"] >= 16 else "LOW", f"{found['ram_total_gb']} GB (reported {reported.ram_gb} GB)"))
    notes.append(("Free disk", "OK" if found["disk_free_gb"] >= 30 else "LOW", f"{found['disk_free_gb']} GB free"))
    models = found["ollama_models"]
    if models is None:
        notes.append(("Ollama", "NOT REACHABLE", "Start Ollama, then run this again"))
    else:
        has = any((m or "").startswith("llama3.2") for m in models)
        notes.append(("Ollama", "OK" if has else "NO LLAMA 3.2", ", ".join(models) or "no models installed"))
    notes.append(("Microphone", "OK" if found["microphones"] else "NOT FOUND", found["microphones"] or "none detected"))
    return notes


def main():
    found = scan()
    lines = [f"Archie laptop scan  {datetime.now():%Y-%m-%d %H:%M}", "Read-only. Nothing was changed or uploaded.", ""]
    lines += [f"{k}: {v}" for k, v in found.items()]
    lines += ["", "Checks:"] + [f"  [{status}] {name}: {detail}" for name, status, detail in verdicts(found)]
    text = "\n".join(lines)
    print(text)
    desktop = Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop"
    target = (desktop if desktop.is_dir() else Path.home()) / "ArchieLaptopReport.txt"
    target.write_text(text, encoding="utf-8")
    print(f"\nSaved to {target}")
    if getattr(sys, "frozen", False):
        input("\nPress Enter to close.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
