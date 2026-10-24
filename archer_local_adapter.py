"""Local authenticated transport adapter for ARCHER.

Uses the existing signed loopback transport. No public network listener.
"""
from archer_secure_transport import make_packet, send_loopback

class LocalAdapter:
    def __init__(self, port, secret, source):
        if not isinstance(port, int) or not 1 <= port <= 65535:
            raise ValueError('Invalid port')
        if not isinstance(secret, bytes) or len(secret) < 32:
            raise ValueError('Secret must be at least 32 bytes')
        if not isinstance(source, str) or not source.strip():
            raise ValueError('Invalid source')
        self.port = port
        self.secret = secret
        self.source = source

    def __call__(self, device_id, department, message):
        if device_id != self.source:
            raise PermissionError('Adapter source mismatch')
        import uuid
        event = {'id': uuid.uuid4().hex, 'source': self.source,
                 'department': department, 'payload': message}
        return send_loopback(self.port, make_packet(self.secret, event))
