"""Read-only simulated install compatibility check for reported HP laptop specs."""
from dataclasses import dataclass, asdict
import json

@dataclass(frozen=True)
class Laptop:
    os: str
    cpu: str
    ram_gb: int
    ssd_gb: int
    touchscreen: bool
    architecture: str = "unverified"
    free_disk_gb: int | None = 3530
    python_version: str = "unverified"
    ollama_installed: bool = False

REPORTED_HP = Laptop("Windows 11 Pro build 26200; HP Laptop 17-cp3xxx; SKU B97RFUA#ABA; BIOS F.15; board 8DC4", "AMD Ryzen 5 7430U (6 cores, 12 threads)", 64, 4096, True, architecture="x64")

def simulate_install(laptop=REPORTED_HP):
    checks = [
        {"component": "Windows GUI", "result": "compatible_on_paper" if "Windows 11" in laptop.os else "needs_verification", "reason": "Tkinter supported on Windows with Python Tcl/Tk"},
        {"component": "CPU and RAM", "result": "compatible_on_paper" if laptop.ram_gb >= 16 else "needs_verification", "reason": "64 GB RAM reported; actual free memory and model benchmarks not measured"},
        {"component": "Windows installer EXE", "result": "needs_verification", "reason": "Installer wizard does not install the complete ARCHER system; EXE must be smoke-tested on Windows"},
        {"component": "Python runtime", "result": "needs_verification" if laptop.python_version == "unverified" else "present_reported", "reason": "Python installation and Tcl/Tk availability not measured"},
        {"component": "Free storage", "result": "needs_verification" if laptop.free_disk_gb is None else ("compatible_on_paper" if laptop.free_disk_gb >= 30 else "insufficient"), "reason": "SSD capacity is not available free disk space"},
        {"component": "Local AI model", "result": "needs_verification", "reason": "Ollama installation, model files and actual response speed not verified"},
        {"component": "Windows architecture", "result": "needs_verification" if laptop.architecture == "unverified" else "reported", "reason": "Actual 64-bit Windows system type not captured"},
        {"component": "App Control for Business", "result": "needs_verification", "reason": "Owner screenshot shows enforced App Control policy; unsigned or untrusted packaged executable may be blocked"},
        {"component": "Virtualization-based security", "result": "compatible_on_paper", "reason": "Owner screenshot confirms VBS and hypervisor-enforced code integrity running; do not disable protections"},
        {"component": "Drive encryption status", "result": "needs_verification", "reason": "Windows C: shows a padlock icon; confirm actual BitLocker/device encryption protection status before installation"},
        {"component": "Available RAM", "result": "compatible_on_paper", "reason": "Owner screenshot shows 49.4 GB available physical memory and 50.8 GB available virtual memory at capture time"},
        {"component": "Android APK", "result": "not_implemented", "reason": "No verified APK build and device test"},
        {"component": "Private login and encryption", "result": "not_implemented", "reason": "Local SQLite notes are not encrypted; do not enter sensitive information"},
        {"component": "Microphone and hardware", "result": "not_implemented", "reason": "Microphone, diagnostics adapters and cameras not integrated"},
    ]
    return {"simulation_only": True, "device_scanned": False, "laptop": asdict(laptop), "checks": checks, "ready_to_install_complete_system": False}

if __name__ == "__main__":
    print(json.dumps(simulate_install(), indent=2))
