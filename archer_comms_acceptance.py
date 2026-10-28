"""Local-only end-to-end ARCHER communications acceptance test and CLI.

Starts a loopback receiver, enrolls simulated devices, persists outbound messages,
retries delivery, revokes one source and verifies that no revoked messages arrive.
No real devices, public listener, accounts or internet are used.
"""
import argparse
import json
import secrets
import tempfile
from pathlib import Path
from archer_durable_queue import DurableQueue
from archer_secure_transport import LocalReceiver, LoopbackServer, make_packet, send_loopback
from archer_remote_relay import DeviceRegistry

def run_acceptance():
    registry = DeviceRegistry()
    for name, kind in (("VAL","val"),("Phone","android-phone"),("Truck Radio","android-radio"),("Fenix 8","garmin-watch"),("Venu 3S","garmin-watch")):
        registry.enroll(name, kind)
    secret = secrets.token_bytes(32)
    receiver = LocalReceiver(secret, registry.allowed())
    with tempfile.TemporaryDirectory() as temp:
        queue = DurableQueue(Path(temp)/"events.db")
        for source, department in (("VAL","Shop"),("Phone","Hunting"),("Truck Radio","VAL"),("Fenix 8","Supervisor"),("Venu 3S","Supervisor")):
            queue.enqueue(source,department,"simulated status")
        server = LoopbackServer(receiver).start()
        try:
            first = queue.flush(registry.allowed(), lambda event: send_loopback(server.port, make_packet(secret,event)))
            remaining_after_first = len(queue.pending())
            registry.revoke("Truck Radio")
            receiver.allowed_sources = registry.allowed()
            queue.enqueue("Truck Radio","VAL","should never deliver")
            revoked = queue.flush(registry.allowed(),lambda event: send_loopback(server.port,make_packet(secret,event)))
            final = len(queue.pending())
            delivered = len(receiver.messages)
        finally:
            server.close()
    passed = first == 5 and remaining_after_first == 0 and revoked == 0 and final == 0 and delivered == 5
    return {"passed":passed,"delivered":delivered,"devices_enrolled":5,"revocation_blocked":revoked==0,"pending":final,"scope":"simulation-only loopback"}

def main():
    parser=argparse.ArgumentParser(description="ARCHER local communication acceptance")
    parser.parse_args()
    result=run_acceptance()
    print(json.dumps(result,indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
