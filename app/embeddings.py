import hashlib,re
from collections import Counter
import numpy as np

class HashEmbeddingModel:
    """Deterministic local embedding fallback with no external model download."""
    def __init__(self,dimensions=384): self.dimensions=dimensions
    def _tokens(self,text): return re.findall(r"[\wÀ-ž]+",text.lower())
    def encode(self,texts):
        out=[]
        for text in texts:
            v=np.zeros(self.dimensions,dtype=np.float32)
            tokens=self._tokens(text)
            counts=Counter(tokens)
            for token,count in counts.items():
                digest=hashlib.blake2b(token.encode(),digest_size=8).digest()
                idx=int.from_bytes(digest[:4],"little")%self.dimensions
                sign=1.0 if digest[4]&1 else -1.0
                v[idx]+=sign*(1+np.log1p(count))
            n=np.linalg.norm(v)
            out.append(v/n if n else v)
        return np.vstack(out) if out else np.empty((0,self.dimensions),dtype=np.float32)

embedding_model=HashEmbeddingModel()
