import hashlib,re
from collections import Counter
import numpy as np
from .config import settings

class HashEmbeddingModel:
    """Deterministic local fallback; useful for offline tests and bootstrap deployments."""
    name="hash-384-v1"
    dimensions=384
    def _tokens(self,text):
        return re.findall(r"[\wÀ-ž\u0900-\u097F]+",text.lower())
    def encode(self,texts):
        out=[]
        for text in texts:
            v=np.zeros(self.dimensions,dtype=np.float32)
            counts=Counter(self._tokens(text))
            for token,count in counts.items():
                digest=hashlib.blake2b(token.encode("utf-8"),digest_size=8).digest()
                idx=int.from_bytes(digest[:4],"little")%self.dimensions
                sign=1.0 if digest[4]&1 else -1.0
                v[idx]+=sign*(1+np.log1p(count))
            n=np.linalg.norm(v)
            out.append(v/n if n else v)
        return np.vstack(out) if out else np.empty((0,self.dimensions),dtype=np.float32)

class SentenceTransformerEmbeddingModel:
    """Optional learned multilingual encoder. Model loading is lazy."""
    dimensions=384
    def __init__(self,model_name):
        self.name=model_name
        self._model=None
    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model=SentenceTransformer(self.name)
        return self._model
    def encode(self,texts):
        if not texts:return np.empty((0,self.dimensions),dtype=np.float32)
        vectors=np.asarray(self._load().encode(list(texts),normalize_embeddings=True,show_progress_bar=False),dtype=np.float32)
        if vectors.shape[1]!=self.dimensions:
            raise ValueError(f"Embedding dimension {vectors.shape[1]} is incompatible with pgvector dimension {self.dimensions}")
        return vectors

def build_embedding_model():
    provider=settings.embedding_provider
    if provider=="sentence-transformers":
        try:return SentenceTransformerEmbeddingModel(settings.embedding_model)
        except ImportError:
            if settings.embedding_strict: raise
    return HashEmbeddingModel()

embedding_model=build_embedding_model()
