"""Persistent project and conversation memory stored in ARCHER's shared local database."""
from datetime import datetime, timezone
from bulldawg_core import managed_connection

def _schema(db):
    db.execute("""CREATE TABLE IF NOT EXISTS memory_events (
        id INTEGER PRIMARY KEY, department TEXT NOT NULL,
        kind TEXT NOT NULL, project TEXT NOT NULL,
        content TEXT NOT NULL, created TEXT NOT NULL
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS memory_events_project ON memory_events(project, id)")

def remember(content, *, department="Supervisor", kind="note", project="general"):
    if not isinstance(content, str) or not content.strip() or len(content) > 50000:
        raise ValueError("Memory content must be 1-50000 characters")
    for field in (department, kind, project):
        if not isinstance(field, str) or not field.strip() or len(field) > 200:
            raise ValueError("Invalid memory metadata")
    with managed_connection() as db:
        _schema(db)
        cursor = db.execute(
            "INSERT INTO memory_events(department,kind,project,content,created) VALUES(?,?,?,?,?)",
            (department, kind, project, content.strip(), datetime.now(timezone.utc).isoformat()))
        return cursor.lastrowid

def recall(*, project=None, query=None, limit=50):
    if not isinstance(limit, int) or not 1 <= limit <= 500:
        raise ValueError("Limit must be between 1 and 500")
    sql = "SELECT id,department,kind,project,content,created FROM memory_events WHERE 1=1"
    params = []
    if project is not None:
        sql += " AND project=?"
        params.append(project)
    if query is not None:
        sql += " AND instr(lower(content), lower(?)) > 0"
        params.append(query)
    sql += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with managed_connection() as db:
        _schema(db)
        rows = db.execute(sql, params).fetchall()
    keys = ("id", "department", "kind", "project", "content", "created")
    return [dict(zip(keys, row)) for row in rows]
