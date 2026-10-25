"""Reproducible local stress run. Never contacts GitHub or external services."""
import concurrent.futures
import hashlib
import io
import json
import os
from pathlib import Path
import random
import sys
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(ROOT / 'tests')]
from archer_platform import http_response, launch_application
from archer_secure_transport import LocalReceiver, make_packet

MODULES = ['test_rg6_platform_security', 'test_rg6_hardening',
           'test_archer_remote_relay', 'test_archer_runtime_check', 'test_archer_model']

def fd_count():
    path = Path('/proc/self/fd')
    return len(list(path.iterdir())) if path.exists() else None

def run(rounds=1000):
    randomizer = random.Random(20261025)
    start = time.monotonic()
    # Initialize optional runtime/Tk libraries before measuring repeated-run leaks.
    startup = {'threads': threading.active_count(), 'fds': fd_count()}
    warmup = unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(
        unittest.defaultTestLoader.loadTestsFromNames(MODULES))
    if not warmup.wasSuccessful() or warmup.skipped:
        raise AssertionError('Warm-up suite failed')
    before = {'threads': threading.active_count(), 'fds': fd_count()}
    total = 0
    for iteration in range(rounds):
        modules = list(MODULES)
        randomizer.shuffle(modules)
        suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output, verbosity=0).run(suite)
        total += result.testsRun
        if not result.wasSuccessful() or result.skipped:
            raise AssertionError('Round ' + str(iteration + 1) + '\n' + output.getvalue())
        if (iteration + 1) % 100 == 0:
            print(f'{iteration + 1}/{rounds} rounds; {total} test executions passed', flush=True)

    # State shared by 16 concurrent callers: retry idempotency and changed-ID rejection.
    key = os.urandom(32)
    receiver = LocalReceiver(key, {'VAL'}, now=lambda: 1000, max_messages=2000)
    packets = [make_packet(key, {'id': str(i), 'source': 'VAL', 'department': 'VAL',
                               'payload': 'test ' + str(i)}, timestamp=1000)
               for i in range(2000)]
    work = packets * 3
    randomizer.shuffle(work)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        assert all(pool.map(receiver.accept, work))
    assert len(receiver.messages) == len(receiver.seen) == 2000
    for i in range(2000):
        changed = make_packet(key, {'id': str(i), 'source': 'VAL', 'department': 'VAL',
                                   'payload': 'tampered'}, timestamp=1000)
        assert receiver.accept(changed) is False

    # Vary hostile URLs/launch strings; no network request or process may be created.
    from unittest.mock import patch
    with patch('archer_platform.http.client.HTTPConnection') as plain, \
            patch('archer_platform.http.client.HTTPSConnection') as tls, \
            patch('archer_platform.subprocess.Popen') as execute:
        for i in range(10000):
            url = randomizer.choice(['file:///private/', 'ftp://example.invalid/',
                                     'http://example.invalid/', 'https://user:pass@example.invalid/']) + str(i)
            try:
                with http_response(url):
                    raise AssertionError('Hostile URL was accepted')
            except ValueError:
                pass
            try:
                launch_application('notepad & echo ' + str(i), owner_approved=True)
                raise AssertionError('Command injection was accepted')
            except ValueError:
                pass
        plain.assert_not_called()
        tls.assert_not_called()
        execute.assert_not_called()

    after = {'threads': threading.active_count(), 'fds': fd_count()}
    assert after['threads'] <= before['threads'], (before, after)
    if before['fds'] is not None:
        assert after['fds'] <= before['fds'] + 1, (before, after)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')}
    report = {'status': 'passed', 'rounds': rounds, 'test_executions': total,
              'skipped': 0, 'concurrent_delivery_attempts': 6000, 'unique_events': 2000,
              'changed_payload_rejections': 2000, 'hostile_url_rejections': 10000,
              'command_injection_rejections': 10000, 'resources_before': before,
              'resources_after': after, 'resources_before_runtime_initialization': startup,
              'warmup_test_executions': warmup.testsRun,
              'elapsed_seconds': round(time.monotonic() - start, 2),
              'source_sha256': hashes,
              'limits': ['Local Linux run; Windows launcher calls mocked.',
                         'No actual Windows installer, model inference, microphone, or laptop test.',
                         'Not the full RG6 suite or a guarantee of future behavior.',
                         'No GitHub upload or installed application change.']}
    destination = ROOT / 'reports'
    destination.mkdir(exist_ok=True)
    (destination / 'RG6-stress-results.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2), flush=True)

if __name__ == '__main__':
    run()
