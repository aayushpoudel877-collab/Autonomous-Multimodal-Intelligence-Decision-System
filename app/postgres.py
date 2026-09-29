import numpy as np

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
                source_id TEXT PRIMARY KEY, model TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW())""")
            cur.execute("CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings USING hnsw (embedding vector_cosine_ops)")
    def save(self,ids,vectors):
        with self.conn.cursor() as cur:
            for sid,vec in zip(ids,vectors):
                cur.execute("INSERT INTO embeddings(source_id,model,embedding) VALUES(%s,%s,%s) ON CONFLICT(source_id) DO UPDATE SET model=EXCLUDED.model,embedding=EXCLUDED.embedding",(sid,self.model_name,np.asarray(vec,dtype=np.float32)))
    def search(self,query,ids,k=5):
        if not ids:return np.zeros(0,dtype=np.float32)
        q=np.asarray(query,dtype=np.float32)
        with self.conn.cursor() as cur:
            cur.execute("SELECT source_id,1-(embedding<=>%s) AS score FROM embeddings WHERE source_id=ANY(%s) ORDER BY embedding<=>%s LIMIT %s",(q,ids,q,k))
            scores={sid:float(score) for sid,score in cur.fetchall()}
        return np.asarray([scores.get(sid,0.0) for sid in ids],dtype=np.float32)
