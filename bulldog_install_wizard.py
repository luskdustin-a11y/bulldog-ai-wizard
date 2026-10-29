#!/usr/bin/env python3
"""
Bulldawg AI Install Wizard
Windows-style setup wizard for the Bulldawg AI laptop system.
Owner-approved actions only. Local logging to %USERPROFILE%\\.bulldog_ai\\
"""

import os
import sys
import hashlib
import subprocess
import webbrowser
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import platform
import shutil
import importlib.util
import threading
import json

VERSION = "1.4.0"
LOG_DIR = Path(os.path.expanduser("~")) / ".bulldog_ai"
LOG_FILE = LOG_DIR / "wizard.log"

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{platform.node()}] {msg}\n")
    print(msg)

class BulldogWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"Bulldawg AI Install Wizard v{VERSION}")
        self.geometry("640x480")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.current_step = 0
        self.selected_components = {}
        self.install_finished = False
        self.install_attempted = False
        self.install_in_progress = False
        self.steps = [
            self.screen_welcome,
            self.screen_system_check,
            self.screen_components,
            self.screen_web_search,
            self.screen_progress,
            self.screen_done,
        ]

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        self.show_step()

    def show_step(self):
        for w in self.container.winfo_children():
            w.destroy()
        self.steps[self.current_step]()

    def next_step(self):
        if self.install_in_progress:
            return
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            self.show_step()

    def screen_welcome(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ascii_art = """
  ____        _ _     _                      _    ___
 | __ ) _   _| | | __| | __ ___      ____ _  / \\  |_ _|
 |  _ \\| | | | | |/ _` |/ _` \\ \\ /\\ / / _` |/ _ \\  | |
 | |_) | |_| | | | (_| | (_| |\\ V  V / (_| / ___ \\ | |
 |____/ \\__,_|_|_|\\__,_|\\__,_| \\_/\\_/ \\__,_/_/   \\_\\___|
        """
        ttk.Label(frame, text=ascii_art, font=("Courier", 9), justify="center").pack(pady=10)
        ttk.Label(frame, text="Bulldawg AI Install Wizard", font=("Segoe UI", 16, "bold")).pack()
        ttk.Label(frame, text="Owner-only Windows laptop setup\nHP 17-inch touchscreen target", justify="center").pack(pady=5)
        ttk.Label(frame, text=f"Version {VERSION}  |  Local logs: {LOG_DIR}", font=("Segoe UI", 8)).pack(pady=10)

        ttk.Button(frame, text="Next >", command=self.next_step).pack(side="bottom", pady=10)

    def screen_system_check(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="System Check", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))

        text = scrolledtext.ScrolledText(frame, height=15, state="disabled")
        text.pack(fill="both", expand=True)

        def append(msg):
            text.config(state="normal")
            text.insert("end", msg + "\n")
            text.config(state="disabled")
            text.see("end")
            self.update()

        append(f"OS: {platform.system()} {platform.release()}")
        append(f"Architecture: {platform.machine()}")
        append(f"Python: {sys.version.split()[0]}")
        total, used, free = shutil.disk_usage(Path.home().anchor)
        append(f"Disk free: {free // (1024**3)} GB")
        append(f"Write access to {LOG_DIR}: {'OK' if os.access(LOG_DIR, os.W_OK) else 'DENIED'}")
        try:
            urllib.request.urlopen("https://www.google.com", timeout=3)
            append("Internet: Available")
        except Exception:
            append("Internet: Unavailable (optional features limited)")

        log("System check completed")
        ttk.Button(frame, text="Next >", command=self.next_step).pack(side="bottom", pady=10)

    def screen_components(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Component Selection", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))
        ttk.Label(frame, text="Select packages to install (requires explicit approval later):").pack(anchor="w")

        packages = ["pySerial", "Pillow", "Requests", "FORScan (official page)", "Python (winget)", "Git (winget)", "VS Code (winget)"]
        self.vars = {}
        for pkg in packages:
            var = tk.BooleanVar(value=False)
            self.vars[pkg] = var
            ttk.Checkbutton(frame, text=pkg, variable=var).pack(anchor="w", padx=20)

        ttk.Button(frame, text="Next >", command=self.next_step).pack(side="bottom", pady=10)

    def screen_web_search(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Optional Web Search / Download", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))
        ttk.Label(frame, text="Find Windows software through Microsoft's winget catalog.\nDiscovery never installs software. Approval is required for installation.").pack(anchor="w")

        self.search_entry = ttk.Entry(frame, width=50)
        self.search_entry.pack(pady=10)
        self.search_entry.insert(0, "Python")

        ttk.Button(frame, text="Find software in winget catalog", command=self.do_search).pack()
        self.search_results = scrolledtext.ScrolledText(frame, height=11, width=72)
        self.search_results.pack(fill="both", expand=True, pady=8)
        self.search_results.insert("end", "Search results appear here. Choose known packages on the previous screen to install.\n")
        ttk.Label(frame, text="Only exact, approved catalog IDs can be installed.", font=("Segoe UI", 8)).pack(pady=5)

        ttk.Button(frame, text="Next >", command=self.next_step).pack(side="bottom", pady=10)

    def do_search(self):
        q = self.search_entry.get().strip()
        if not q:
            return
        if not shutil.which("winget"):
            self.search_results.insert("end", "Windows Package Manager (winget) not found.\n")
            return
        self.search_results.delete("1.0", "end")
        self.search_results.insert("end", f"Searching official winget catalog for {q}...\n")
        def worker():
            try:
                result = subprocess.run(["winget", "search", "--query", q, "--source", "winget", "--disable-interactivity"], capture_output=True, text=True, timeout=60)
                msg = (result.stdout or result.stderr or "No results")[-8000:]
                if result.returncode:
                    msg = "Search failed: " + msg
            except Exception as exc:
                msg = "Search failed: " + str(exc)
            self.after(0, lambda: (self.search_results.delete("1.0", "end"), self.search_results.insert("end", msg)))
        threading.Thread(target=worker, daemon=True).start()

    def screen_progress(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Verified Setup", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))
        self.progress = ttk.Progressbar(frame, mode="determinate", length=500)
        self.progress.pack(pady=10)
        self.status = ttk.Label(frame, text="No installations attempted")
        self.status.pack()
        self.install_button = ttk.Button(frame, text="Install Approved Components", command=self.run_installs)
        self.install_button.pack(pady=10)
        self.next_button = ttk.Button(frame, text="Next >", command=self.next_step)
        self.next_button.pack(side="bottom", pady=10)

    def run_installs(self):
        selected = [k for k, v in self.vars.items() if v.get()]
        if not selected:
            messagebox.showinfo("Nothing selected", "No components were selected.")
            return
        if not messagebox.askyesno("Owner approval", "Proceed with these actions?\n\n" + "\n".join(selected) + "\n\nPython packages use the current Python environment. External tools open official vendor pages; no external executable is silently run."):
            return
        self.install_attempted = True
        self.install_in_progress = True
        self.install_finished = False
        self.install_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.progress["value"] = 0
        threading.Thread(target=self._install_worker, args=(selected,), daemon=True).start()

    def _install_worker(self, selected):
        modules = {"pySerial": ("pyserial", "serial"), "Pillow": ("Pillow", "PIL"), "Requests": ("requests", "requests")}
        vendor_pages = {"FORScan (official page)": "https://forscan.org/download.html"}
        winget_packages = {"Python (winget)": "Python.Python.3.13", "Git (winget)": "Git.Git", "VS Code (winget)": "Microsoft.VisualStudioCode"}
        failures = []
        for index, pkg in enumerate(selected):
            self.after(0, lambda name=pkg: self.status.config(text=f"Checking {name}..."))
            if pkg in vendor_pages:
                self.after(0, lambda url=vendor_pages[pkg]: webbrowser.open(url))
                log(f"Opened official vendor page for {pkg}; installation NOT verified")
                failures.append(f"{pkg}: manual vendor installation not verified")
            elif pkg in winget_packages:
                package_id = winget_packages[pkg]
                if not shutil.which("winget"):
                    failures.append(f"{pkg}: winget not installed")
                else:
                    try:
                        check = subprocess.run(["winget", "list", "--id", package_id, "--exact", "--source", "winget", "--disable-interactivity"], capture_output=True, text=True, timeout=45)
                        if check.returncode == 0 and package_id.lower() in check.stdout.lower():
                            log(f"Already present in winget inventory: {package_id}")
                        else:
                            result = subprocess.run(["winget", "install", "--id", package_id, "--exact", "--source", "winget", "--disable-interactivity", "--accept-source-agreements", "--accept-package-agreements"], capture_output=True, text=True, timeout=900)
                            if result.returncode:
                                raise RuntimeError((result.stderr or result.stdout)[-500:])
                            verify = subprocess.run(["winget", "list", "--id", package_id, "--exact", "--disable-interactivity"], capture_output=True, text=True, timeout=45)
                            if verify.returncode or package_id.lower() not in verify.stdout.lower():
                                raise RuntimeError("Installer returned success but installed package not confirmed")
                            log(f"winget installation verified: {package_id}")
                    except Exception as exc:
                        failures.append(f"{pkg}: {exc}")
                        log(f"FAILED {pkg}: {exc}")
            else:
                pip_name, module = modules[pkg]
                if importlib.util.find_spec(module) is not None:
                    log(f"Already installed: {pkg}")
                else:
                    try:
                        result = subprocess.run([sys.executable, "-m", "pip", "install", pip_name], capture_output=True, text=True, timeout=240)
                        if result.returncode != 0:
                            raise RuntimeError((result.stderr or result.stdout)[-500:])
                        # Separate process ensures fresh module visibility
                        check = subprocess.run([sys.executable, "-c", f"import {module}"], capture_output=True, text=True, timeout=30)
                        if check.returncode != 0:
                            raise RuntimeError(check.stderr[-500:])
                        log(f"Installed and import-verified: {pkg}")
                    except Exception as exc:
                        failures.append(f"{pkg}: {exc}")
                        log(f"FAILED {pkg}: {exc}")
            self.after(0, lambda val=round((index+1)*100/len(selected)): self.progress.config(value=val))
        self.after(0, lambda: self._finish_installs(failures))

    def _finish_installs(self, failures):
        self.install_in_progress = False
        self.install_button.config(state="normal")
        self.next_button.config(state="normal")
        if failures:
            self.status.config(text="Incomplete — see details")
            messagebox.showwarning("Setup incomplete", "Not all components are verified:\n\n" + "\n".join(failures))
        else:
            self.install_finished = True
            self.status.config(text="All selected packages verified")
            messagebox.showinfo("Verified", "All selected packages passed verification.")

    def screen_done(self):
        frame = ttk.Frame(self.container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Done + Launch Pad", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0,10))
        ttk.Label(frame, text="Launch pad (not a complete Archie installation):").pack(anchor="w")
        ttk.Label(frame, text=("Selected packages verified" if self.install_finished else "Archie installation NOT verified"), foreground=("green" if self.install_finished else "red")).pack(anchor="w")

        buttons = [
            ("Edge", "msedge"),
            ("Notepad", "notepad"),
            ("File Explorer", "explorer"),
            ("Command Prompt", "cmd"),
        ]
        for label, cmd in buttons:
            state = "normal" if shutil.which(cmd) or (cmd in {"explorer", "notepad", "cmd"}) else "disabled"
            ttk.Button(frame, text=label, state=state,
                       command=lambda c=cmd: self.launch(c)).pack(fill="x", padx=20, pady=2)

        ttk.Label(frame, text=f"Logs written to:\n{LOG_FILE}", font=("Segoe UI", 8)).pack(pady=10)
        ttk.Button(frame, text="Finish", command=self.destroy).pack(side="bottom", pady=10)

    def launch(self, cmd):
        if messagebox.askyesno("Confirm Launch", f"Launch {cmd}?"):
            try:
                if cmd not in {"msedge", "notepad", "explorer", "cmd"}:
                    raise ValueError("Launch target not approved")
                subprocess.Popen([cmd], shell=False)
                log(f"Launched {cmd}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    log(f"Bulldawg AI Wizard {VERSION} started")
    app = BulldogWizard()
    app.mainloop()
    log("Wizard exited")
