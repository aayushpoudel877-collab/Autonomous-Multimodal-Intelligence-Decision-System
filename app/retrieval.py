from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class Retriever:
    def __init__(self): self.v=TfidfVectorizer(ngram_range=(1,2),max_features=12000);self.m=None;self.s=[]
    def rebuild(self,sources):
        self.s=sources;self.m=self.v.fit_transform([x.content for x in sources]) if sources else None
    def search(self,q,k=5):
        if self.m is None:return []
        scores=cosine_similarity(self.v.transform([q]),self.m)[0]
        return [{"source":self.s[i],"score":round(float(scores[i]),4)} for i in scores.argsort()[::-1][:k] if scores[i]>0]
retriever=Retriever()