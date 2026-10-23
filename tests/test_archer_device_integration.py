import unittest
from archer_device_integration import DeviceIntegration

class DeviceIntegrationTests(unittest.TestCase):
    def test_approval_required_and_revocation_blocks_access(self):
        devices = DeviceIntegration()
        devices.register("front-door", "camera", lambda: {"motion": True})
        with self.assertRaises(PermissionError):
            devices.read("front-door")
        devices.approve("front-door")
        result = devices.read("front-door")
        self.assertEqual(result["data"]["motion"], True)
        self.assertEqual(result["category"], "camera")
        devices.revoke("front-door")
        with self.assertRaises(PermissionError):
            devices.read("front-door")

    def test_rejects_invalid_or_duplicate_adapters(self):
        devices = DeviceIntegration()
        with self.assertRaises(ValueError):
            devices.register("unknown", "unsupported", lambda: {})
        devices.register("truck", "vehicle_diagnostics", lambda: {"rpm": 0})
        with self.assertRaises(ValueError):
            devices.register("truck", "vehicle_diagnostics", lambda: {})
        devices.approve("truck")
        self.assertEqual(devices.read("truck")["data"]["rpm"], 0)

    def test_rejects_non_dictionary_telemetry(self):
        devices = DeviceIntegration()
        devices.register("hvac", "thermostat", lambda: "unavailable")
        devices.approve("hvac")
        with self.assertRaises(ValueError):
            devices.read("hvac")

if __name__ == "__main__":
    unittest.main()
