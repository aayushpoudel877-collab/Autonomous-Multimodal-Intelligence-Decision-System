from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .chunking import chunk_source
from .embeddings import embedding_model

class Retriever:
    def __init__(self):
        self.v=TfidfVectorizer(ngram_range=(1,2),max_features=20000,sublinear_tf=True)
        self.tfidf=None
        self.embeddings=None
        self.s=[]

    @property
    def ready(self): return bool(self.s and self.tfidf is not None and self.embeddings is not None)

    def rebuild(self,sources):
        chunks=[]
        for source in sources: chunks.extend(chunk_source(source))
        self.s=chunks
        texts=[x.content for x in chunks]
        self.tfidf=self.v.fit_transform(texts) if texts else None
        self.embeddings=embedding_model.encode(texts) if texts else None

    def search(self,q,k=5):
        if not self.ready or not q.strip(): return []
        lexical=cosine_similarity(self.v.transform([q]),self.tfidf)[0]
        semantic=self.embeddings@embedding_model.encode([q])[0]
        combined=.55*lexical+.45*semantic
        ranked=combined.argsort()[::-1]
        return [{"source":self.s[i],"score":round(float(combined[i]),4),"lexical_score":round(float(lexical[i]),4),"semantic_score":round(float(semantic[i]),4)} for i in ranked[:k] if combined[i]>0]

retriever=Retriever()
