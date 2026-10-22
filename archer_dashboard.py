#!/usr/bin/env python3
"""ARCHER local desktop dashboard. Standard-library only; no network services."""
import tkinter as tk
from tkinter import messagebox, ttk
import bulldawg_core as core
from archer_persona import SYSTEM_NAME

class ArcherDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ARCHER | Private Command Center")
        self.geometry("1050x680")
        self.minsize(760, 500)
        self.configure(bg="#101722")
        self.department = tk.StringVar(value=core.DEPARTMENTS[0])
        self.status = tk.StringVar(value="LOCAL MODE • No AI model connected • No sync")
        self._build()
        self.refresh()

    def _build(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30)
        head = tk.Frame(self, bg="#101722", pady=18)
        head.pack(fill="x", padx=24)
        tk.Label(head, text=SYSTEM_NAME, font=("Segoe UI", 27, "bold"), fg="#f0f4ff", bg="#101722").pack(anchor="w")
        tk.Label(head, textvariable=self.status, fg="#e5bc75", bg="#101722", font=("Segoe UI", 10)).pack(anchor="w")
        main = tk.Frame(self, bg="#101722")
        main.pack(fill="both", expand=True, padx=24, pady=8)
        sidebar = tk.Frame(main, bg="#1b2635", width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 16))
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="DEPARTMENTS", fg="white", bg="#1b2635", font=("Segoe UI", 11, "bold")).pack(pady=(16, 8))
        for dept in core.DEPARTMENTS:
            tk.Radiobutton(sidebar, text=dept, variable=self.department, value=dept, command=self.refresh,
                           anchor="w", padx=12, pady=8, fg="white", bg="#1b2635",
                           selectcolor="#34465c", activebackground="#34465c", activeforeground="white",
                           indicatoron=False, relief="flat").pack(fill="x", padx=8, pady=2)
        panel = tk.Frame(main, bg="#101722")
        panel.pack(side="left", fill="both", expand=True)
        self.heading = tk.Label(panel, text="", fg="white", bg="#101722", font=("Segoe UI", 19, "bold"))
        self.heading.pack(anchor="w", pady=(0, 12))
        tk.Label(panel, text="Local records (not an AI conversation)", fg="#aabbd0", bg="#101722").pack(anchor="w")
        self.records = tk.Listbox(panel, bg="#1b2635", fg="#eaf0fb", selectbackground="#365776",
                                  relief="flat", font=("Segoe UI", 11), height=13)
        self.records.pack(fill="both", expand=True, pady=(8, 12))
        tk.Label(panel, text="New note", fg="#aabbd0", bg="#101722").pack(anchor="w")
        self.entry = tk.Text(panel, height=4, wrap="word", bg="#1b2635", fg="white",
                             insertbackground="white", relief="flat", font=("Segoe UI", 11))
        self.entry.pack(fill="x", pady=(6, 10))
        controls = tk.Frame(panel, bg="#101722")
        controls.pack(fill="x")
        tk.Button(controls, text="Save note", command=self.save, bg="#3a688d", fg="white", padx=18, pady=8).pack(side="left")
        tk.Button(controls, text="Refresh", command=self.refresh, padx=18, pady=8).pack(side="left", padx=10)
        tk.Button(controls, text="System health", command=self.show_health, padx=18, pady=8).pack(side="right")

    def refresh(self):
        dept = self.department.get()
        self.heading.configure(text=dept)
        self.records.delete(0, "end")
        try:
            notes = core.list_notes(dept)
            for note in notes:
                self.records.insert("end", f'{note["created"][:16]}  |  {note["text"].replace(chr(10), " ")}')
            if not notes:
                self.records.insert("end", "No records yet.")
        except Exception as exc:
            messagebox.showerror("Read failed", str(exc))

    def save(self):
        value = self.entry.get("1.0", "end").strip()
        if not value:
            messagebox.showwarning("Empty note", "Enter a note first.")
            return
        try:
            core.add_note(self.department.get(), value)
        except Exception as exc:
            messagebox.showerror("Save failed", str(exc))
            return
        self.entry.delete("1.0", "end")
        self.refresh()

    def show_health(self):
        state = core.health()
        messagebox.showinfo("ARCHER system health",
                            f'Status: {state["status"]}\nMode: {state["mode"]}\n'
                            f'Notes: {state["notes"]}\nDatabase encrypted: {state["encrypted"]}\n'
                            f'AI model connected: {state["ai_model_connected"]}\n'
                            f'Phone sync enabled: {state["phone_sync_enabled"]}')

if __name__ == "__main__":
    ArcherDashboard().mainloop()
