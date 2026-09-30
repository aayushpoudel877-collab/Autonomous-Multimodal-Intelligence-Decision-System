import hashlib,re
from collections import Counter
import numpy as np
from .config import settings

class HashEmbeddingModel:
    """Deterministic local fallback; useful for offline tests and bootstrap deployments."""
    name="hash-384-v1"; dimensions=384
    def _tokens(self,text): return re.findall(r"[\wÀ-ž\u0900-\u097F]+",text.lower())
    def encode(self,texts):
        out=[]
        for text in texts:
            v=np.zeros(self.dimensions,dtype=np.float32)
            counts=Counter(self._tokens(text))
            for token,count in counts.items():
                digest=hashlib.blake2b(token.encode("utf-8"),digest_size=8).digest()
                idx=int.from_bytes(digest[:4],"little")%self.dimensions
                v[idx]+=(1.0 if digest[4]&1 else -1.0)*(1+np.log1p(count))
            n=np.linalg.norm(v); out.append(v/n if n else v)
        return np.vstack(out) if out else np.empty((0,self.dimensions),dtype=np.float32)

class SentenceTransformerEmbeddingModel:
    """Lazy learned multilingual encoder. Falls back only when strict mode is disabled."""
    dimensions=384
    def __init__(self,model_name):
        self.name=model_name; self._model=None
    def _load(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model=SentenceTransformer(self.name)
            except ImportError:
                if settings.embedding_strict: raise
                return None
        return self._model
    def encode(self,texts):
        if not texts:return np.empty((0,self.dimensions),dtype=np.float32)
        model=self._load()
        if model is None:return HashEmbeddingModel().encode(texts)
        vectors=np.asarray(model.encode(list(texts),normalize_embeddings=True,show_progress_bar=False),dtype=np.float32)
        if vectors.ndim!=2 or vectors.shape[1]!=self.dimensions:
            raise ValueError(f"Embedding dimension {vectors.shape[1] if vectors.ndim==2 else 'unknown'} is incompatible with pgvector dimension {self.dimensions}")
        return vectors

def build_embedding_model():
    if settings.embedding_provider=="sentence-transformers":
        return SentenceTransformerEmbeddingModel(settings.embedding_model)
    return HashEmbeddingModel()

embedding_model=build_embedding_model()
