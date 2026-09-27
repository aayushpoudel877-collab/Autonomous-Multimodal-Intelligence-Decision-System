from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .chunking import chunk_source
class Retriever:
    def __init__(self):
        self.v=TfidfVectorizer(ngram_range=(1,2),max_features=20000,sublinear_tf=True)
        self.m=None; self.s=[]
    def rebuild(self,sources):
        chunks=[]
        for source in sources: chunks.extend(chunk_source(source))
        self.s=chunks
        self.m=self.v.fit_transform([x.content for x in chunks]) if chunks else None
    def search(self,q,k=5):
        if self.m is None or not q.strip(): return []
        scores=cosine_similarity(self.v.transform([q]),self.m)[0]
        ranked=scores.argsort()[::-1]
        return [{"source":self.s[i],"score":round(float(scores[i]),4)} for i in ranked[:k] if scores[i]>0]
retriever=Retriever()
