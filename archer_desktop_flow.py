"""Local, offline ARCHER tower visualization for laptop or desktop.

Run: python archer_desktop_flow.py
Uses Tkinter from the Python standard library. Signals are DEMO ONLY.
"""
import tkinter as tk

COMPONENTS = ("CPU", "RAM", "GPU", "SSD", "Cooling", "Network", "Memory AI", "Recovery")
COLORS = {"ok": "#38bdf8", "warning": "#facc15", "failed": "#f87171"}

class TowerFlow:
    def __init__(self, root):
        self.root = root
        self.root.title("ARCHER — Desktop Flow Monitor (Simulation)")
        self.root.geometry("650x650")
        self.state = {name: "ok" for name in COMPONENTS}
        self.canvas = tk.Canvas(root, width=630, height=500, bg="#101827", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=8, pady=8)
        self.status = tk.StringVar(value="DEMO ONLY — not connected to hardware or live module tests.")
        tk.Label(root, textvariable=self.status, wraplength=600).pack(pady=4)
        controls = tk.Frame(root)
        controls.pack(pady=8)
        for label, callback in (("Healthy baseline", self.baseline), ("Warning", self.warning),
                                ("Failure", self.failure), ("Simulated recheck", self.recheck)):
            tk.Button(controls, text=label, command=callback).pack(side="left", padx=3)
        self.draw()
    def draw(self):
        c = self.canvas
        c.delete("all")
        c.create_polygon(105,40,420,40,510,95,510,455,175,455,105,400,
                         fill="#263346", outline="#a5b4c8", width=3)
        c.create_line(105,40,175,95,510,95,fill="#a5b4c8",width=2)
        c.create_line(175,95,175,455,fill="#a5b4c8",width=2)
        c.create_rectangle(190,110,480,435,fill="#142d40",outline="#4d839d",width=2)
        coords = [(215+(i%2)*136,135+(i//2)*73) for i in range(8)]
        for i in range(7):
            a,b=coords[i],coords[i+1]
            c.create_line(a[0]+53,a[1]+24,b[0]+53,b[1]+24,fill=COLORS[self.state[COMPONENTS[i+1]]],width=4,dash=(9,6),arrow="last")
        for name,(x,y) in zip(COMPONENTS,coords):
            c.create_rectangle(x,y,x+116,y+48,fill="#182435",outline=COLORS[self.state[name]],width=3)
            c.create_text(x+58,y+24,text=name,fill="white",font=("Arial",11,"bold"))
        c.create_text(310,20,text="ARCHER — VIRTUAL COMPUTER",fill="white",font=("Arial",15,"bold"))
        c.create_text(310,477,text="Blue: OK   Yellow: Warning   Red: Failure   •   Simulation",fill="#cbd5e1")
    def baseline(self):
        if any(v=="failed" for v in self.state.values()):
            self.status.set("Failure remains red until a passing simulated recheck.")
            return
        self.state = dict.fromkeys(COMPONENTS,"ok")
        self.status.set("Simulated baseline reset. No real tests executed.")
        self.draw()
    def warning(self):
        self.state["Cooling"]="warning"
        self.status.set("Simulated cooling warning. No hardware temperature was measured.")
        self.draw()
    def failure(self):
        self.state["SSD"]="failed"
        self.status.set("Simulated SSD failure. No physical drive was tested.")
        self.draw()
    def recheck(self):
        self.state["SSD"]="ok"
        self.status.set("Simulated recheck passed for SSD; no actual repair performed.")
        self.draw()

def main():
    root=tk.Tk()
    TowerFlow(root)
    root.mainloop()

if __name__=="__main__":
    main()
