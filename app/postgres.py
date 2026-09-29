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

class PostgresVectorRepository:
    model_name="hash-384-v1"
    def __init__(self,url):
        if not url: raise ValueError("AEGISMIND_POSTGRES_URL is required")
        import psycopg
        from pgvector.psycopg import register_vector
        self.conn=psycopg.connect(url,autocommit=True)
        register_vector(self.conn)
        with self.conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("""CREATE TABLE IF NOT EXISTS embeddings(
                source_id TEXT PRIMARY KEY,model TEXT NOT NULL,
                embedding vector(384) NOT NULL,created_at TIMESTAMPTZ DEFAULT NOW())""")
            cur.execute("CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings USING hnsw (embedding vector_cosine_ops)")
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
