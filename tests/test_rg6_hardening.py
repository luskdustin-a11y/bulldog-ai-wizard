import io
import math
import ssl
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import contextmanager

from archer_platform import http_response, launch_application
from archer_runtime_check import inspect_local_machine
from archer_secure_transport import LocalReceiver, make_packet, sign


class HardeningTests(unittest.TestCase):
    def test_runtime_rejects_malformed_model_catalog_without_crash(self):
        samples = [b'null', b'[]', b'{"models":null}', b'{"models":[null]}',
                   b'{"models":[{"name":[]}] }', b'{"models":{}}',
                   b'{"models":[]}' + b' ' * 200001]
        for raw in samples:
            with self.subTest(raw=raw[:40]):
                @contextmanager
                def fake(*args, **kwargs):
                    yield io.BytesIO(raw)
                with patch('archer_runtime_check.http_response', fake):
                    result = inspect_local_machine()
                self.assertFalse(result['local_model_server'])
                self.assertEqual(result['model_names'], [])

    def test_runtime_accepts_valid_catalog(self):
        @contextmanager
        def fake(*args, **kwargs):
            yield io.BytesIO(b'{"models":[{"name":"existing-3b"}]}')
        with patch('archer_runtime_check.http_response', fake):
            result = inspect_local_machine()
        self.assertTrue(result['local_model_server'])
        self.assertEqual(result['model_names'], ['existing-3b'])

    def test_insecure_tls_context_rejected_before_connect(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with patch('archer_platform.http.client.HTTPSConnection') as connection:
            with self.assertRaises(ValueError):
                with http_response('https://approved.example/', context=context):
                    pass
            connection.assert_not_called()

    def test_windows_batch_file_never_launched(self):
        executable = str(Path(tempfile.gettempdir()) / 'notepad.cmd')
        with patch('archer_platform.shutil.which', return_value=executable), \
                patch('archer_platform.subprocess.Popen') as execute:
            with self.assertRaises(ValueError):
                launch_application('notepad', owner_approved=True)
            execute.assert_not_called()

    def test_current_directory_cannot_shadow_approved_application(self):
        for filename in ['notepad.exe', str(Path.cwd() / 'notepad.exe')]:
            with patch('archer_platform.shutil.which', return_value=filename), \
                    patch('archer_platform.subprocess.Popen') as execute:
                with self.assertRaises(ValueError):
                    launch_application('notepad', owner_approved=True)
                execute.assert_not_called()

    def test_non_finite_packet_timestamps_rejected(self):
        key = b'x' * 32
        receiver = LocalReceiver(key, {'VAL'}, now=lambda: 1000)
        for timestamp in [math.nan, math.inf, -math.inf, 10**400, -1, True]:
            packet = make_packet(key, {'id': '1', 'source': 'VAL', 'department': 'VAL', 'payload': 'test'}, timestamp=timestamp)
            self.assertFalse(receiver.accept(packet))

    def test_malformed_packet_strings_rejected_without_crash(self):
        key = b'x' * 32
        receiver = LocalReceiver(key, {'VAL'}, now=lambda: 1000)
        packet = make_packet(key, {'id': '1', 'source': 'VAL', 'department': 'VAL', 'payload': 'test'}, timestamp=1000)
        packet['signature'] = '\u00e9'
        self.assertFalse(receiver.accept(packet))
        packet['envelope']['payload'] = '\ud800'
        packet['signature'] = sign(key, packet['envelope'])
        self.assertFalse(receiver.accept(packet))

    def test_capacity_rejects_new_events_but_allows_exact_retry(self):
        key = b'x' * 32
        receiver = LocalReceiver(key, {'VAL'}, now=lambda: 1000, max_messages=1)
        event = {'id': '1', 'source': 'VAL', 'department': 'VAL', 'payload': 'test'}
        first = make_packet(key, event, timestamp=1000)
        self.assertTrue(receiver.accept(first))
        self.assertTrue(receiver.accept(first))
        event['id'] = '2'
        self.assertFalse(receiver.accept(make_packet(key, event, timestamp=1000)))
        self.assertEqual(len(receiver.messages), 1)
        first['envelope']['payload'] = 'mutated after acceptance'
        self.assertEqual(receiver.messages[0]['payload'], 'test')


if __name__ == '__main__':
    unittest.main()
