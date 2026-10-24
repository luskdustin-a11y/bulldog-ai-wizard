"""Deterministic 5,000-event ARCHER communication stress and failure test.

Software simulation only. No real devices, public network or remote services.
"""
import json
import random
import secrets
import tempfile
from pathlib import Path
from archer_durable_queue import DurableQueue
from archer_secure_transport import LocalReceiver, make_packet

TOTAL=5000
SOURCES=("VAL","Phone","Truck Radio","Fenix 8","Venu 3S")
DEPARTMENTS=("val","hunting","shop","supervisor","finances","stocks","property","hotshot")

def run_stress(total=TOTAL, seed=20261022):
    rng=random.Random(seed)
    key=secrets.token_bytes(32)
    receiver=LocalReceiver(key,set(SOURCES))
    attempts=0
    offline=0
    with tempfile.TemporaryDirectory() as folder:
        queue=DurableQueue(Path(folder)/"stress.db")
        for i in range(total):
            queue.enqueue(SOURCES[i%len(SOURCES)],DEPARTMENTS[i%len(DEPARTMENTS)],"stress-"+str(i))
        def intermittent(event):
            nonlocal attempts,offline
            attempts+=1
            if rng.random()<0.15:
                offline+=1
                raise ConnectionError("simulated network outage")
            return receiver.accept(make_packet(key,event))
        rounds=0
        while queue.pending() and rounds<25:
            queue.flush(set(SOURCES),intermittent)
            rounds+=1
        remaining=len(queue.pending())
        accepted=len(receiver.messages)
        ids={event["id"] for event in receiver.messages}
        return {"passed":remaining==0 and accepted==total and len(ids)==total,
                "total":total,"accepted":accepted,"unique":len(ids),
                "remaining":remaining,"attempts":attempts,
                "simulated_outages":offline,"retry_rounds":rounds,
                "scope":"offline software stress simulation"}

if __name__=="__main__":
    report=run_stress()
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report["passed"] else 1)
