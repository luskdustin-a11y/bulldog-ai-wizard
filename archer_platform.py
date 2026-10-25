"""Shared platform adapter: bounded HTTP without redirects/proxies and shell-free launch.

Callers retain owner approval, stop, audit and permission checks. This adapter
does not grant authority or claim full shared-core integration of legacy RG6.
"""
from contextlib import contextmanager
import http.client
import os
from pathlib import Path
import shutil
import ssl
import subprocess
from urllib.parse import urlsplit
from urllib.error import HTTPError

LAUNCHERS = frozenset({'chrome', 'msedge', 'notepad', 'explorer', 'torque', 'cmd'})

@contextmanager
def http_response(url, *, method='GET', data=None, headers=None, timeout=10,
                  allowed_hosts=None, allow_loopback_http=False, context=None):
    if not isinstance(url, str) or any(ord(c) <= 32 or ord(c) == 127 for c in url) or '\\' in url:
        raise ValueError('Invalid HTTP URL')
    parsed = urlsplit(url)
    host = parsed.hostname
    loopback = host in {'127.0.0.1', 'localhost', '::1'}
    if (not host or parsed.username is not None or parsed.password is not None
            or parsed.fragment or parsed.scheme not in {'https', 'http'}
            or (parsed.scheme == 'http' and not (allow_loopback_http and loopback))):
        raise ValueError('HTTPS or explicitly permitted loopback HTTP required')
    if allowed_hosts is not None and host not in allowed_hosts:
        raise ValueError('Unapproved HTTP host')
    if (method not in {'GET', 'POST'} or type(timeout) not in {int, float}
            or not 0 < timeout <= 120):
        raise ValueError('Invalid HTTP method or timeout')
    if data is not None and (not isinstance(data, bytes) or len(data) > 1_048_576):
        raise ValueError('Invalid or oversized request body')
    port = parsed.port  # Reject malformed/out-of-range ports before connecting.
    if parsed.scheme == 'https':
        if context is not None and (not isinstance(context, ssl.SSLContext)
                or not context.check_hostname or context.verify_mode != ssl.CERT_REQUIRED):
            raise ValueError('TLS certificate and hostname verification required')
        connection = http.client.HTTPSConnection(host, port, timeout=timeout,
                                                 context=context or ssl.create_default_context())
    else:
        connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        target = parsed.path or '/'
        if parsed.query:
            target += '?' + parsed.query
        connection.request(method, target, body=data, headers=headers or {})
        response = connection.getresponse()
        # Never follow redirects with owner credentials or signed packets.
        if not 200 <= response.status < 300:
            response.close()
            raise HTTPError(url, response.status, 'HTTP request rejected', response.headers, None)
        with response:
            yield response
    finally:
        connection.close()

def launch_application(name, *, owner_approved=False):
    if owner_approved is not True:
        raise PermissionError('Owner approval required')
    if name not in LAUNCHERS:
        raise ValueError('Unapproved application')
    executable = shutil.which(name)
    if not executable:
        raise FileNotFoundError('Application is unavailable')
    candidate = Path(executable)
    if not candidate.is_absolute() or candidate.resolve().parent == Path.cwd().resolve():
        raise ValueError('Current-directory and relative launch targets are not approved')
    # Windows may execute batch wrappers through a shell even with shell=False.
    if candidate.suffix.lower() in {'.bat', '.cmd', '.ps1'}:
        raise ValueError('Script wrappers are not approved launch targets')
    if os.name == 'nt' and candidate.suffix.lower() != '.exe':
        raise ValueError('Windows launch target must be an executable')
    return subprocess.Popen([executable], shell=False)
