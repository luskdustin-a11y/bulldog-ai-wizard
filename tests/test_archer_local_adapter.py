import secrets
import unittest
from archer_local_adapter import LocalAdapter
from archer_secure_transport import LocalReceiver, LoopbackServer
from archer_universal_hub import UniversalHub

class LocalAdapterTests(unittest.TestCase):
    def test_authenticated_delivery(self):
        secret = secrets.token_bytes(32)
        receiver = LocalReceiver(secret, {'laptop'})
        server = LoopbackServer(receiver).start()
        try:
            hub = UniversalHub()
            hub.enroll('laptop', 'windows', {'shop'})
            hub.register_adapter('local', LocalAdapter(server.port, secret, 'laptop'))
            self.assertTrue(hub.send('laptop', 'shop', 'local', 'hello'))
            self.assertEqual(receiver.messages[0]['payload'], 'hello')
        finally:
            server.close()

    def test_reject_spoofed_device(self):
        secret = secrets.token_bytes(32)
        adapter = LocalAdapter(1234, secret, 'laptop')
        with self.assertRaises(PermissionError):
            adapter('another-device', 'shop', 'hello')

    def test_invalid_secret(self):
        with self.assertRaises(ValueError):
            LocalAdapter(1234, b'short', 'laptop')
