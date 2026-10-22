import io
import json
import unittest
from archer_local_ai import OllamaEngine,LocalModelUnavailable
from archer_device_bridge import DeviceBridge

class FakeResponse:
    status=200
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def read(self,limit): return b'{"message":{"content":"The injector test passed."}}'

class IntegrationTests(unittest.TestCase):
    def test_local_model_response(self):
        def fake(req,timeout):
            self.assertEqual(req.full_url,"http://127.0.0.1:11434/api/chat")
            self.assertEqual(json.loads(req.data)["stream"],False)
            return FakeResponse()
        ai=OllamaEngine(opener=fake)
        self.assertEqual(ai.answer("Injector?","shop"),"The injector test passed.")

    def test_external_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            OllamaEngine(endpoint="https://cloud.example.com")

    def test_model_offline_error(self):
        from urllib.error import URLError
        def fail(req,timeout): raise URLError("offline")
        with self.assertRaises(LocalModelUnavailable):
            OllamaEngine(opener=fail).answer("test","shop")

    def test_device_routes_only_authorized_department(self):
        bridge=DeviceBridge()
        bridge.enroll("my-phone","android-phone",{"hunting"})
        result=bridge.request("my-phone","hunting","camera status")
        self.assertIn("not installed",result["answer"])
        with self.assertRaises(PermissionError):
            bridge.request("my-phone","finances","accounts")

    def test_device_revocation(self):
        bridge=DeviceBridge()
        bridge.enroll("my-radio","android-radio",{"val"})
        bridge.revoke("my-radio")
        with self.assertRaises(PermissionError):
            bridge.request("my-radio","val","hello")

    def test_device_inventory(self):
        bridge=DeviceBridge()
        bridge.enroll("watch","garmin-watch",{"supervisor"})
        self.assertEqual(bridge.inventory()[0]["type"],"garmin-watch")
