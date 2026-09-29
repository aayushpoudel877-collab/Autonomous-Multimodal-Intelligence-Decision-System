import json,sqlite3
from pathlib import Path
from threading import Lock
from .schemas import Source

class SQLiteStore:
    def __init__(self,path:str):
        self.path=path; Path(path).parent.mkdir(parents=True,exist_ok=True); self.lock=Lock(); self._init_db()
    def _connect(self):
        con=sqlite3.connect(self.path,check_same_thread=False); con.row_factory=sqlite3.Row; return con
    def _init_db(self):
        with self._connect() as con:
            con.execute("CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY,title TEXT NOT NULL,content TEXT NOT NULL,metadata TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            con.execute("CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT,action TEXT NOT NULL,subject_id TEXT,details TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            con.execute("CREATE TABLE IF NOT EXISTS embeddings(source_id TEXT PRIMARY KEY,model TEXT NOT NULL,dimension INTEGER NOT NULL,vector TEXT NOT NULL,created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
            con.execute("""CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY,type TEXT NOT NULL,status TEXT NOT NULL,payload TEXT NOT NULL,
                result TEXT,error TEXT,attempts INTEGER NOT NULL DEFAULT 0,max_attempts INTEGER NOT NULL DEFAULT 3,
                idempotency_key TEXT UNIQUE,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,finished_at TEXT)""")
            con.commit()
    def upsert(self,source:Source):
        with self.lock,self._connect() as con:
            con.execute("INSERT OR REPLACE INTO sources(id,title,content,metadata) VALUES(?,?,?,?)",(source.id,source.title,source.content,json.dumps(source.metadata)))
            con.execute("INSERT INTO audit_log(action,subject_id,details) VALUES(?,?,?)",("source.upsert",source.id,json.dumps({"title":source.title}))); con.commit()
        return source
    def all(self):
        with self._connect() as con: rows=con.execute("SELECT id,title,content,metadata FROM sources ORDER BY created_at,id").fetchall()
        return [Source(id=r["id"],title=r["title"],content=r["content"],metadata=json.loads(r["metadata"])) for r in rows]
    def save_embeddings(self,ids,vectors,model):
        rows=[(sid,model,len(vec),json.dumps([float(x) for x in vec])) for sid,vec in zip(ids,vectors)]
        with self.lock,self._connect() as con:
            con.executemany("INSERT OR REPLACE INTO embeddings(source_id,model,dimension,vector) VALUES(?,?,?,?)",rows); con.commit()
    def load_embeddings(self,model):
        with self._connect() as con: rows=con.execute("SELECT source_id,vector FROM embeddings WHERE model=?",(model,)).fetchall()
        return {r["source_id"]:json.loads(r["vector"]) for r in rows}
    def audit(self,limit=100):
        with self._connect() as con: rows=con.execute("SELECT id,action,subject_id,details,created_at FROM audit_log ORDER BY id DESC LIMIT ?",(limit,)).fetchall()
        return [dict(r) for r in rows]
    def create_job(self,job_id,job_type,payload,idempotency_key,max_attempts=3):
        with self.lock,self._connect() as con:
            if idempotency_key:
                row=con.execute("SELECT * FROM jobs WHERE idempotency_key=?",(idempotency_key,)).fetchone()
                if row:return dict(row)
            con.execute("INSERT INTO jobs(id,type,status,payload,max_attempts,idempotency_key) VALUES(?,?,?,?,?,?)",(job_id,job_type,"queued",json.dumps(payload),max_attempts,idempotency_key))
            row=con.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone(); con.commit()
        return dict(row)
    def update_job(self,job_id,**fields):
        allowed={"status","result","error","attempts","started_at","finished_at","updated_at"}
        fields={k:v for k,v in fields.items() if k in allowed}
        if not fields:return self.get_job(job_id)
        fields["updated_at"]="CURRENT_TIMESTAMP"
        assignments=[]; values=[]
        for k,v in fields.items():
            if v=="CURRENT_TIMESTAMP": assignments.append(f"{k}=CURRENT_TIMESTAMP")
            else: assignments.append(f"{k}=?"); values.append(json.dumps(v) if k=="result" else v)
        values.append(job_id)
        with self.lock,self._connect() as con:
            con.execute(f"UPDATE jobs SET {','.join(assignments)} WHERE id=?",values); con.commit()
        return self.get_job(job_id)
    def get_job(self,job_id):
        with self._connect() as con: row=con.execute("SELECT * FROM jobs WHERE id=?",(job_id,)).fetchone()
        return dict(row) if row else None
    def list_jobs(self,limit=50):
        with self._connect() as con: rows=con.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
        return [dict(r) for r in rows]
