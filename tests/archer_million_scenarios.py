"""Deterministic, isolated ARCHER routing simulations (not full-system acceptance)."""
import json
import os
import random
import time
from pathlib import Path
from archer_department_hub import DepartmentHub, Request, DEPARTMENTS

def main():
    n=int(os.environ.get("SIM_ITERATIONS","1000000"))
    if not 1 <= n <= 5000000:
        raise ValueError("SIM_ITERATIONS must be between 1 and 5,000,000")
    rng=random.Random(20261022)
    hub=DepartmentHub()
    names=sorted(DEPARTMENTS)
    for department in names:
        hub.enroll("sim-"+department,{department})
        hub.register(department,lambda question: "simulated:"+question)
    failures=[]
    counts={"authorized":0,"denied":0,"revoked":0}
    start=time.monotonic()
    for i in range(n):
        dept=names[rng.randrange(len(names))]
        mode=i%20
        try:
            if mode==0:
                try:
                    hub.route(Request("unknown",dept,"ping"))
                    raise AssertionError("Unknown device accepted")
                except PermissionError:
                    counts["denied"]+=1
            elif mode==1:
                other=names[(names.index(dept)+1)%len(names)]
                try:
                    hub.route(Request("sim-"+dept,other,"ping"))
                    raise AssertionError("Cross-department access accepted")
                except PermissionError:
                    counts["denied"]+=1
            elif mode==2:
                device="temp-"+str(i)
                hub.enroll(device,{dept})
                hub.revoke(device)
                try:
                    hub.route(Request(device,dept,"ping"))
                    raise AssertionError("Revoked device accepted")
                except PermissionError:
                    counts["revoked"]+=1
            else:
                answer=hub.route(Request("sim-"+dept,dept,"ping"))
                assert answer["status"]=="handled" and answer["answer"]=="simulated:ping"
                counts["authorized"]+=1
        except Exception as exc:
            failures.append({"iteration":i,"error":repr(exc)})
            break
    report={"commit":os.environ.get("GITHUB_SHA","local"),"target":n,
            "executed":sum(counts.values()),"counts":counts,
            "failures":failures,"duration_seconds":round(time.monotonic()-start,3),
            "scope":"department routing and access-control simulation only",
            "full_system_verified":False}
    Path("archer-million-report.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
    if failures or report["executed"]!=n:
        raise SystemExit(1)

if __name__=="__main__":
    main()
