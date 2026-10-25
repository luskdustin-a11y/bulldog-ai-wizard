"""Authenticated loopback-only ARCHER transport prototype.

This is not an internet relay, VPN, phone or Garmin integration.
Requires explicit operator-provided shared secret; never opens a public listener.
"""
import hashlib
import hmac
import json
import math
import secrets
import socket
import socketserver
import threading
import time

MAX_BYTES = 65536
CLOCK_SKEW = 120

def sign(secret, envelope):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("Secret must be at least 32 bytes")
    body = json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(secret, body, hashlib.sha256).hexdigest()

class LocalReceiver:
    def __init__(self, secret, allowed_sources, now=time.time, *, max_messages=10000):
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError("Secret must be at least 32 bytes")
        self.secret = secret
        if type(max_messages) is not int or not 1 <= max_messages <= 100000:
            raise ValueError('Invalid message capacity')
        self.max_messages = max_messages
        self.allowed_sources = set(allowed_sources)
        self.now = now
        self.seen = {}
        self.messages = []
        self.lock = threading.Lock()

    def accept(self, packet):
        if not isinstance(packet, dict) or set(packet) != {"envelope", "signature"}:
            return False
        env = packet["envelope"]
        if not isinstance(env, dict) or set(env) != {"id", "source", "department", "payload", "timestamp", "nonce"}:
            return False
        if not all(isinstance(env[k], str) and env[k] for k in ("id","source","department","payload","nonce")):
            return False
        try:
            payload_bytes = env['payload'].encode('utf-8')
        except UnicodeError:
            return False
        if (env["source"] not in self.allowed_sources or len(payload_bytes) > MAX_BYTES
                or any(len(env[k]) > 256 for k in ('id', 'source', 'department', 'nonce'))):
            return False
        if not isinstance(env["timestamp"], (int,float)) or isinstance(env["timestamp"], bool):
            return False
        if isinstance(env['timestamp'], float) and not math.isfinite(env['timestamp']):
            return False
        if not 0 <= env['timestamp'] <= 1_000_000_000_000_000:
            return False
        if abs(self.now() - env["timestamp"]) > CLOCK_SKEW:
            return False
        signature = packet['signature']
        if (not isinstance(signature, str) or len(signature) != 64
                or any(c not in '0123456789abcdef' for c in signature)
                or not hmac.compare_digest(sign(self.secret, env), signature)):
            return False
        fingerprint = (env["source"], env["department"], env["payload"])
        with self.lock:
            if env["id"] in self.seen:
                return self.seen[env["id"]] == fingerprint  # reject ID reuse with changed contents
            if len(self.messages) >= self.max_messages:
                return False  # Backpressure; never discard accepted history silently.
            self.seen[env["id"]] = fingerprint
            self.messages.append(dict(env))
        return True

def make_packet(secret, event, timestamp=None):
    envelope = {k:event[k] for k in ("id","source","department","payload")}
    envelope.update(timestamp=time.time() if timestamp is None else timestamp, nonce=secrets.token_hex(16))
    return {"envelope":envelope,"signature":sign(secret,envelope)}

class LoopbackServer:
    def __init__(self, receiver):
        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                data = self.rfile.readline(MAX_BYTES + 2048)
                try:
                    if len(data) > MAX_BYTES + 2047 or not data.endswith(b"\n"):
                        raise ValueError("oversized or incomplete")
                    accepted = receiver.accept(json.loads(data))
                except (ValueError, TypeError, KeyError, UnicodeDecodeError):
                    accepted = False
                self.wfile.write(b'{"accepted":true}\n' if accepted else b'{"accepted":false}\n')
        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True
        self.server = Server(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def port(self):
        return self.server.server_address[1]

    def start(self):
        self.thread.start()
        return self

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

def send_loopback(port, packet, timeout=2):
    data = (json.dumps(packet, separators=(",", ":")) + "\n").encode()
    if len(data) > MAX_BYTES + 2048:
        raise ValueError("Packet too large")
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(data)
        with sock.makefile("rb") as reader:
            response = reader.readline(256)
    return json.loads(response)["accepted"] is True
