import unittest
from archer_universal_hub import UniversalHub

class UniversalHubTests(unittest.TestCase):
    def test_enrollment_and_routing(self):
        hub = UniversalHub()
        hub.enroll('laptop', 'windows', {'shop'})
        self.assertEqual(hub.ask('laptop', 'shop', 'hello')['department'], 'shop')

    def test_adapter_delivery(self):
        hub = UniversalHub()
        hub.enroll('phone', 'android', {'val'})
        hub.register_adapter('test', lambda device, dept, msg: (device, dept, msg))
        self.assertEqual(hub.send('phone', 'val', 'test', 'hello'), ('phone', 'val', 'hello'))

    def test_unauthorized_department(self):
        hub = UniversalHub()
        hub.enroll('watch', 'garmin', {'supervisor'})
        hub.register_adapter('test', lambda *args: 'ok')
        with self.assertRaises(PermissionError):
            hub.send('watch', 'finances', 'test', 'secret')

    def test_revocation(self):
        hub = UniversalHub()
        hub.enroll('tablet', 'ios', {'shop'})
        hub.revoke('tablet')
        with self.assertRaises(PermissionError):
            hub.ask('tablet', 'shop', 'hello')

    def test_duplicate_device(self):
        hub = UniversalHub()
        hub.enroll('laptop', 'linux', {'shop'})
        with self.assertRaises(ValueError):
            hub.enroll('laptop', 'linux', {'shop'})

    def test_unregistered_adapter(self):
        hub = UniversalHub()
        hub.enroll('laptop', 'windows', {'shop'})
        with self.assertRaises(LookupError):
            hub.send('laptop', 'shop', 'missing', 'hello')

    def test_cannot_replace_registered_adapter(self):
        hub = UniversalHub()
        hub.register_adapter('secure', lambda *args: 'original')
        with self.assertRaises(ValueError):
            hub.register_adapter('secure', lambda *args: 'replacement')
