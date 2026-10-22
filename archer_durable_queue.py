"""Simulation-only persistent outbound event queue. No network calls."""
import sqlite3
import uuid
from pathlib import Path

class DurableQueue:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, source TEXT NOT NULL, department TEXT NOT NULL, payload TEXT NOT NULL, state TEXT NOT NULL DEFAULT "pending")')

    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def enqueue(self, source, department, payload):
        if not all(isinstance(x, str) and x.strip() for x in (source, department, payload)):
            raise ValueError('source, department and payload must be nonempty strings')
        if len(payload.encode('utf-8')) > 65536:
            raise ValueError('payload too large')
        event_id = uuid.uuid4().hex
        with self._connect() as db:
            db.execute('INSERT INTO events(id,source,department,payload,state) VALUES (?,?,?,?,?)', (event_id, source, department, payload, 'pending'))
        return event_id

    def pending(self):
        with self._connect() as db:
            return [{'id': row[0], 'source': row[1], 'department': row[2], 'payload': row[3]} for row in db.execute('SELECT id,source,department,payload FROM events WHERE state=? ORDER BY rowid', ('pending',))]

    def acknowledge(self, event_id):
        with self._connect() as db:
            result = db.execute('UPDATE events SET state=? WHERE id=? AND state=?', ('delivered', event_id, 'pending'))
            return result.rowcount == 1

    def revoke(self, source):
        with self._connect() as db:
            result = db.execute('UPDATE events SET state=? WHERE source=? AND state=?', ('revoked', source, 'pending'))
            return result.rowcount

    def flush(self, authorized_sources, send):
        """ACK only on explicit success; receivers must deduplicate by stable event ID."""
        count = 0
        for event in self.pending():
            if event['source'] not in authorized_sources:
                self.revoke(event['source'])
                continue
            try:
                accepted = send(event)
            except (ConnectionError, TimeoutError, OSError):
                continue
            if accepted is True and self.acknowledge(event['id']):
                count += 1
        return count
