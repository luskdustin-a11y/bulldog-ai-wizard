"""Opt-in ARCHER HTTPS relay service.

For testing only: run behind a separately configured TLS termination proxy.
Never expose the raw HTTP listener to the internet. No listener starts on import.
"""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from archer_secure_transport import LocalReceiver

MAX_REQUEST=70000

def make_handler(receiver):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path != "/v1/events":
                self.send_error(404)
                return
            try:
                size=int(self.headers.get("Content-Length","-1"))
                if size < 0 or size > MAX_REQUEST:
                    self.send_error(413)
                    return
                packet=json.loads(self.rfile.read(size))
                accepted=receiver.accept(packet)
            except (ValueError,TypeError,UnicodeDecodeError,KeyError):
                accepted=False
            body=json.dumps({"accepted":accepted}).encode()
            self.send_response(200 if accepted else 403)
            self.send_header("Content-Type","application/json")
            self.send_header("Content-Length",str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, format, *args):
            return  # avoid logging potentially sensitive request details
    return Handler

def create_server(secret, allowed_sources, host="127.0.0.1", port=0):
    if host not in ("127.0.0.1","::1","localhost"):
        raise ValueError("Raw HTTP relay is restricted to loopback")
    receiver=LocalReceiver(secret,allowed_sources)
    return ThreadingHTTPServer((host,port),make_handler(receiver)),receiver

def main():
    parser=argparse.ArgumentParser(description="ARCHER loopback relay, requires TLS proxy for remote use")
    parser.add_argument("--port",type=int,default=8765)
    parser.add_argument("--sources",default="VAL,Phone")
    args=parser.parse_args()
    secret_hex=os.environ.get("ARCHER_RELAY_SECRET_HEX","")
    try:
        secret=bytes.fromhex(secret_hex)
    except ValueError:
        parser.error("ARCHER_RELAY_SECRET_HEX must contain a hex-encoded secret")
    if len(secret)<32:
        parser.error("Set ARCHER_RELAY_SECRET_HEX to a securely generated 32+ byte secret")
    server,_=create_server(secret,set(args.sources.split(",")),port=args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0

if __name__=="__main__":
    raise SystemExit(main())
