import json
import threading
import tempfile
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError

from archer_platform import http_response, launch_application
from archer_remote_relay import RemoteRelay
from archer_master_report import get_json


class PlatformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302 if self.path == '/redirect' else 200)
                self.send_header('Location', 'file:///private')
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            def log_message(self, *args):
                pass
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=lambda: cls.server.serve_forever(poll_interval=0.01), daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def test_unsafe_urls_rejected_before_connection(self):
        urls = ['file:///etc/passwd', 'ftp://example.com/file', 'http://example.com',
                'https://user:password@example.com', 'https://example.com/#fragment',
                'https://example.com/\r\nInjected: yes', 'https://example.com\\evil',
                'https://example.com:99999/']
        with patch('archer_platform.http.client.HTTPSConnection') as connection:
            for url in urls:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    with http_response(url):
                        pass
            connection.assert_not_called()

    def test_loopback_requires_explicit_permission(self):
        with self.assertRaises(ValueError):
            with http_response(self.base):
                pass

    def test_actual_loopback_ignores_proxy_environment(self):
        with patch.dict('os.environ', {'HTTP_PROXY': 'http://127.0.0.1:1',
                                      'ALL_PROXY': 'http://127.0.0.1:1', 'NO_PROXY': ''}):
            with http_response(self.base, allow_loopback_http=True,
                               allowed_hosts={'127.0.0.1'}) as response:
                self.assertEqual(json.loads(response.read(100)), {'ok': True})

    def test_redirect_never_followed(self):
        with self.assertRaises(HTTPError) as error:
            with http_response(self.base + '/redirect', allow_loopback_http=True):
                pass
        self.assertEqual(error.exception.code, 302)

    def test_host_policy_blocks_before_connection(self):
        with self.assertRaises(ValueError):
            with http_response('https://unapproved.example/', allowed_hosts={'api.github.com'}):
                pass

    def test_launch_requires_owner_and_rejects_command_injection(self):
        with patch('archer_platform.subprocess.Popen') as execute:
            with self.assertRaises(PermissionError):
                launch_application('notepad')
            with self.assertRaises(ValueError):
                launch_application('notepad & calc', owner_approved=True)
            execute.assert_not_called()

    def test_approved_launch_is_argument_list_without_shell(self):
        executable = str(Path(tempfile.gettempdir()) / 'approved-launcher' / 'notepad.exe')
        with patch('archer_platform.shutil.which', return_value=executable), \
                patch('archer_platform.subprocess.Popen') as execute:
            launch_application('notepad', owner_approved=True)
            execute.assert_called_once_with([executable], shell=False)

    def test_report_rejects_paths_and_limits_response(self):
        with patch('archer_master_report.http_response') as transport:
            with self.assertRaises(ValueError):
                get_json('//evil.example/')
            transport.assert_not_called()
            transport.return_value.__enter__.return_value.read.return_value = b'x' * 2_000_001
            with self.assertRaises(ValueError):
                get_json('/repos/owner/repo/actions/runs')
            self.assertEqual(transport.call_args.kwargs['allowed_hosts'], {'api.github.com'})

    def test_relay_uses_shared_platform_transport(self):
        with patch('archer_remote_relay.http_response') as transport:
            response = transport.return_value.__enter__.return_value
            response.status = 200
            response.read.return_value = b'{"accepted":true}'
            relay = RemoteRelay('https://approved.example/api', b'x' * 32)
            self.assertTrue(relay.send({'id': '1', 'source': 'VAL', 'department': 'VAL', 'payload': 'test'}))
            self.assertEqual(transport.call_args.kwargs['method'], 'POST')
            response.read.return_value = b'x' * 1025
            self.assertFalse(relay.send({'id': '2', 'source': 'VAL', 'department': 'VAL', 'payload': 'test'}))


if __name__ == '__main__':
    unittest.main()
