"""Read-only Windows hardware compatibility report. Does not expose serial numbers."""
import json
import os
import platform
import shutil
import subprocess
import sys

def powershell(command):
    try:
        p = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", command], capture_output=True, text=True, timeout=15)
        if p.returncode:
            return {"status": "error", "message": p.stderr[-180:]}
        return {"status": "ok", "data": json.loads(p.stdout)}
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"status": "unavailable", "message": type(exc).__name__}

def collect():
    report = {"mode": "read_only", "physical_hardware_verified": False, "system": platform.system(), "architecture": platform.machine(), "python": sys.version.split()[0], "components": {}}
    if os.name != "nt":
        report["note"] = "Windows-only hardware inventory; no physical hardware verified"
        return report
    queries = {
        "computer": "Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,TotalPhysicalMemory | ConvertTo-Json -Compress",
        "processor": "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress",
        "operating_system": "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,OSArchitecture,Version | ConvertTo-Json -Compress",
        "memory": "Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed | ConvertTo-Json -Compress",
        "storage": "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,Size,FreeSpace | ConvertTo-Json -Compress",
        "graphics": "Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion | ConvertTo-Json -Compress",
        "audio": "Get-CimInstance Win32_SoundDevice | Select-Object Name,Status | ConvertTo-Json -Compress",
        "camera": "Get-PnpDevice -Class Camera -ErrorAction SilentlyContinue | Select-Object FriendlyName,Status | ConvertTo-Json -Compress",
        "bluetooth": "Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | Select-Object FriendlyName,Status | ConvertTo-Json -Compress",
        "usb": "Get-PnpDevice -Class USB -ErrorAction SilentlyContinue | Select-Object FriendlyName,Status | ConvertTo-Json -Compress",
        "battery": "Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Select-Object Name,BatteryStatus | ConvertTo-Json -Compress",
        "touchscreen": "Get-PnpDevice -Class HIDClass -ErrorAction SilentlyContinue | Where-Object FriendlyName -Match 'touch screen' | Select-Object FriendlyName,Status | ConvertTo-Json -Compress"
    }
    for key, query in queries.items():
        report["components"][key] = powershell(query)
    report["physical_hardware_verified"] = False
    report["note"] = "Inventory only; manufacturer stress tests and interactive device tests remain necessary"
    return report

if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
