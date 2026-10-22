import io
import json
import secrets
import unittest
from archer_remote_relay import RemoteRelay, DeviceRegistry

class Response:
    status=200
    def __init__(self, value):
        self.value=value
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self, limit): return self.value[:limit]

class RelayTests(unittest.TestCase):
    def setUp(self):
        self.key=secrets.token_bytes(32)
        self.event={"id":"1","source":"VAL","department":"VAL","payload":"test"}

    def test_http_blocked(self):
        with self.assertRaises(ValueError):
            RemoteRelay("http://example.com/api",self.key)

    def test_embedded_credentials_blocked(self):
        with self.assertRaises(ValueError):
            RemoteRelay("https://u:p@example.com/api",self.key)

    def test_invalid_key_blocked(self):
        with self.assertRaises(ValueError):
            RemoteRelay("https://example.com/api",b"short")

    def test_signed_https_request(self):
        def fake(request,context,timeout):
            self.assertEqual(request.get_method(),"POST")
            self.assertEqual(request.full_url,"https://example.com/api")
            self.assertEqual(json.loads(request.data)["envelope"]["payload"],"test")
            self.assertIsNotNone(context)
            return Response(b'{"accepted":true}')
        self.assertTrue(RemoteRelay("https://example.com/api",self.key,opener=fake).send(self.event))

    def test_negative_ack_retains(self):
        relay=RemoteRelay("https://example.com/api",self.key,opener=lambda *args,**kwargs:Response(b'{"accepted":false}'))
        self.assertFalse(relay.send(self.event))

    def test_enrollment_revocation(self):
        r=DeviceRegistry()
        r.enroll("my-phone","android-phone")
        r.enroll("truck","val")
        self.assertEqual(r.allowed(),{"my-phone","truck"})
        r.revoke("truck")
        self.assertEqual(r.allowed(),{"my-phone"})
        with self.assertRaises(ValueError):
            r.enroll("my-phone","android-phone")
