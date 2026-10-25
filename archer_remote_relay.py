"""Opt-in HTTPS remote relay client. No endpoints, credentials, or connections by default.

Production deployment needs a separately provisioned TLS server, device enrollment,
secret storage and an independent security review. Never use plain HTTP.
"""
import json
import ssl
import urllib.parse
import urllib.request
from archer_secure_transport import make_packet
from archer_platform import http_response

class RemoteRelay:
    def __init__(self, endpoint, secret, ca_file=None, opener=None):
        parsed = urllib.parse.urlsplit(endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("Remote relay requires an HTTPS endpoint without embedded credentials")
        if len(secret) < 32:
            raise ValueError("32-byte or longer secret required")
        self.endpoint = endpoint
        self.secret = secret
        self.ca_file = ca_file
        self.opener = opener

    def send(self, event):
        packet = make_packet(self.secret, event)
        data = json.dumps(packet, separators=(",", ":")).encode("utf-8")
        req = urllib.request.Request(self.endpoint, data=data, headers={"Content-Type":"application/json"}, method="POST")
        ctx = ssl.create_default_context(cafile=self.ca_file)
        # Injection is for offline tests only; default uses certificate-verified HTTPS.
        response = (self.opener(req, context=ctx, timeout=10) if self.opener else
                    http_response(self.endpoint, method='POST', data=data,
                                  headers={'Content-Type': 'application/json'},
                                  context=ctx, timeout=10))
        with response as reply:
            if reply.status != 200:
                return False
            body = reply.read(1025)
        if len(body) > 1024:
            return False
        try:
            answer = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            return False
        return isinstance(answer, dict) and answer.get("accepted") is True

class DeviceRegistry:
    """Explicit device enrollment and revocation; does not discover real devices."""
    TYPES = {"windows", "android-phone", "android-radio", "garmin-watch", "val", "shop"}
    def __init__(self):
        self.devices = {}
    def enroll(self, device_id, device_type):
        if not isinstance(device_id,str) or not device_id.strip() or device_type not in self.TYPES:
            raise ValueError("Invalid device")
        if device_id in self.devices:
            raise ValueError("Device already registered")
        self.devices[device_id] = {"type":device_type, "active":True}
    def revoke(self, device_id):
        if device_id not in self.devices:
            raise KeyError(device_id)
        self.devices[device_id]["active"] = False
    def allowed(self):
        return {k for k,v in self.devices.items() if v["active"]}
