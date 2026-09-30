import json
import numpy as np
from .schemas import Source

class PostgresConnection:
    def __init__(self,url):
        if not url: raise ValueError("AEGISMIND_POSTGRES_URL is required")
        import psycopg
        self.conn=psycopg.connect(url,autocommit=True)
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""CREATE TABLE IF NOT EXISTS sources(
                id TEXT PRIMARY KEY,title TEXT NOT NULL,content TEXT NOT NULL,
                metadata JSONB NOT NULL,created_at TIMESTAMPTZ DEFAULT NOW())""")
            cur.execute("""CREATE TABLE IF NOT EXISTS audit_log(
                id BIGSERIAL PRIMARY KEY,action TEXT NOT NULL,subject_id TEXT,
                details JSONB NOT NULL,created_at TIMESTAMPTZ DEFAULT NOW())""")
            cur.execute("""CREATE TABLE IF NOT EXISTS jobs(
                id TEXT PRIMARY KEY,type TEXT NOT NULL,status TEXT NOT NULL,payload JSONB NOT NULL,
                result JSONB,error TEXT,attempts INTEGER NOT NULL DEFAULT 0,max_attempts INTEGER NOT NULL DEFAULT 3,
                idempotency_key TEXT UNIQUE,created_at TIMESTAMPTZ DEFAULT NOW(),updated_at TIMESTAMPTZ DEFAULT NOW(),
                started_at TIMESTAMPTZ,finished_at TIMESTAMPTZ)""")
    def close(self):
        if getattr(self,"conn",None) and not self.conn.closed:self.conn.close()

class PostgresStore(PostgresConnection):
    def upsert(self,source:Source):
        with self.conn.cursor() as cur:
            cur.execute("""INSERT INTO sources(id,title,content,metadata) VALUES(%s,%s,%s,%s)
                ON CONFLICT(id) DO UPDATE SET title=EXCLUDED.title,content=EXCLUDED.content,metadata=EXCLUDED.metadata""",
                (source.id,source.title,source.content,json.dumps(source.metadata)))
            cur.execute("INSERT INTO audit_log(action,subject_id,details) VALUES(%s,%s,%s)",
                ("source.upsert",source.id,json.dumps({"title":source.title})))
        return source
    def all(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id,title,content,metadata FROM sources ORDER BY created_at,id")
            rows=cur.fetchall()
        return [Source(id=r[0],title=r[1],content=r[2],metadata=r[3] or {}) for r in rows]
    def audit(self,limit=100):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id,action,subject_id,details,created_at FROM audit_log ORDER BY id DESC LIMIT %s",(limit,))
            rows=cur.fetchall()
        return [{"id":r[0],"action":r[1],"subject_id":r[2],"details":r[3],"created_at":r[4]} for r in rows]
    def create_job(self,job_id,job_type,payload,idempotency_key,max_attempts=3):
        with self.conn.cursor() as cur:
            if idempotency_key:
                cur.execute("SELECT id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at FROM jobs WHERE idempotency_key=%s",(idempotency_key,))
                row=cur.fetchone()
                if row:return self._job(row)
            cur.execute("""INSERT INTO jobs(id,type,status,payload,max_attempts,idempotency_key)
                VALUES(%s,%s,'queued',%s,%s,%s)
                RETURNING id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at""",
                (job_id,job_type,json.dumps(payload),max_attempts,idempotency_key))
            return self._job(cur.fetchone())
    def claim_job(self,job_id):
        with self.conn.cursor() as cur:
            cur.execute("""UPDATE jobs SET status='running',attempts=attempts+1,started_at=NOW(),updated_at=NOW(),error=NULL
                WHERE id=%s AND status IN ('queued','retrying')
                RETURNING id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at""",(job_id,))
            row=cur.fetchone()
        return self._job(row)

    def update_job(self,job_id,**fields):
        allowed={"status","result","error","attempts","started_at","finished_at"}
        fields={k:v for k,v in fields.items() if k in allowed}
        if not fields:return self.get_job(job_id)
        sets=[]; vals=[]
        for k,v in fields.items():
            sets.append(f"{k}=%s"); vals.append(json.dumps(v) if k=="result" else v)
        sets.append("updated_at=NOW()"); vals.append(job_id)
        with self.conn.cursor() as cur:
            cur.execute(f"UPDATE jobs SET {','.join(sets)} WHERE id=%s RETURNING id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at",vals)
            row=cur.fetchone()
        return self._job(row)
    def get_job(self,job_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at FROM jobs WHERE id=%s",(job_id,))
            row=cur.fetchone()
        return self._job(row) if row else None
    def list_jobs(self,limit=50):
        with self.conn.cursor() as cur:
            cur.execute("SELECT id,type,status,payload,result,error,attempts,max_attempts,idempotency_key,created_at,updated_at,started_at,finished_at FROM jobs ORDER BY created_at DESC LIMIT %s",(limit,))
            return [self._job(r) for r in cur.fetchall()]
    @staticmethod
    def _job(r):
        if not r:return None
        keys=["id","type","status","payload","result","error","attempts","max_attempts","idempotency_key","created_at","updated_at","started_at","finished_at"]
        return dict(zip(keys,r))

class PostgresVectorRepository(PostgresConnection):
    model_name="hash-384-v1"
    def __init__(self,url):
        super().__init__(url)
        with self.conn.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS embeddings(
                source_id TEXT PRIMARY KEY,model TEXT NOT NULL,
                embedding vector(384) NOT NULL,created_at TIMESTAMPTZ DEFAULT NOW())""")
            cur.execute("CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings USING hnsw (embedding vector_cosine_ops)")
        from pgvector.psycopg import register_vector
        register_vector(self.conn)
    def save(self,ids,vectors):
        with self.conn.cursor() as cur:
            for sid,vec in zip(ids,vectors):
                cur.execute("""INSERT INTO embeddings(source_id,model,embedding) VALUES(%s,%s,%s)
                    ON CONFLICT(source_id) DO UPDATE SET model=EXCLUDED.model,embedding=EXCLUDED.embedding""",
                    (sid,self.model_name,np.asarray(vec,dtype=np.float32)))
    def search(self,query,ids,k=5):
        if not ids:return np.zeros(0,dtype=np.float32)
        q=np.asarray(query,dtype=np.float32); limit=max(k*8,50)
        with self.conn.cursor() as cur:
            cur.execute("""SELECT source_id,1-(embedding<=>%s) AS score
                FROM embeddings WHERE source_id=ANY(%s)
                ORDER BY embedding<=>%s LIMIT %s""",(q,ids,q,limit))
            scores={sid:float(score) for sid,score in cur.fetchall()}
        return np.asarray([scores.get(sid,0.0) for sid in ids],dtype=np.float32)
