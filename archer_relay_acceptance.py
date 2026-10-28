"""End-to-end relay acceptance over real HTTP on loopback.

This exercises queue persistence, signing, server verification and acknowledgements.
No public network or physical devices are contacted.
"""
import http.client
import json
import secrets
import tempfile
import threading
from pathlib import Path
from archer_durable_queue import DurableQueue
from archer_relay_server import create_server
from archer_secure_transport import make_packet

def run_relay_acceptance():
    secret=secrets.token_bytes(32)
    server,receiver=create_server(secret,{"VAL","Phone"})
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try:
        with tempfile.TemporaryDirectory() as directory:
            queue=DurableQueue(Path(directory)/"outbound.db")
            queue.enqueue("VAL","Shop","simulated diagnostics")
            queue.enqueue("Phone","Hunting","simulated camera event")
            def send(event):
                conn=http.client.HTTPConnection("127.0.0.1",server.server_address[1],timeout=3)
                try:
                    packet=make_packet(secret,event)
                    conn.request("POST","/v1/events",json.dumps(packet),{"Content-Type":"application/json"})
                    response=conn.getresponse()
                    result=json.loads(response.read())
                    return response.status==200 and result.get("accepted") is True
                finally:
                    conn.close()
            delivered=queue.flush({"VAL","Phone"},send)
            pending=len(queue.pending())
            receiver.allowed_sources.remove("Phone")
            queue.enqueue("Phone","Hunting","must be rejected")
            # Revocation must be applied to sender and receiver; revoked queue entries are dropped.
            blocked=queue.flush({"VAL"},send)==0
            return {"passed":delivered==2 and pending==0 and blocked and len(receiver.messages)==2,
                    "delivered":delivered,"pending":pending,"revocation_blocked":blocked,
                    "mode":"loopback HTTP integration; remote HTTPS deployment not tested"}
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)

if __name__=="__main__":
    result=run_relay_acceptance()
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result["passed"] else 1)
