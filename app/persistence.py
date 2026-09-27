import json
import os
import sqlite3
from pathlib import Path
from threading import Lock
from .schemas import Source

class SQLiteStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = Lock()
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.path, check_same_thread=False)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL,
                metadata TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            con.execute("""CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL,
                subject_id TEXT, details TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )""")
            con.commit()

    def upsert(self, source: Source):
        with self.lock, self._connect() as con:
            con.execute("INSERT OR REPLACE INTO sources(id,title,content,metadata) VALUES(?,?,?,?)",
                        (source.id, source.title, source.content, json.dumps(source.metadata)))
            con.execute("INSERT INTO audit_log(action,subject_id,details) VALUES(?,?,?)",
                        ("source.upsert", source.id, json.dumps({"title": source.title})))
            con.commit()
        return source

    def all(self):
        with self._connect() as con:
            rows = con.execute("SELECT id,title,content,metadata FROM sources ORDER BY created_at,id").fetchall()
        return [Source(id=r["id"], title=r["title"], content=r["content"], metadata=json.loads(r["metadata"])) for r in rows]

    def audit(self, limit=100):
        with self._connect() as con:
            rows = con.execute("SELECT id,action,subject_id,details,created_at FROM audit_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
