import hashlib
from pathlib import Path
from .config import settings

class LocalObjectStorage:
    def __init__(self,root=None):
        self.root=Path(root or settings.object_storage_dir); self.root.mkdir(parents=True,exist_ok=True)
    def put(self,data:bytes,filename:str="object.bin"):
        digest=hashlib.sha256(data).hexdigest(); suffix=Path(filename).suffix[:20]; path=self.root/f"{digest}{suffix}"
        if not path.exists(): path.write_bytes(data)
        return {"key":path.name,"sha256":digest,"size":len(data)}
    def get(self,key:str)->bytes:
        path=self.root/Path(key).name
        if not path.exists(): raise FileNotFoundError(key)
        return path.read_bytes()
    def delete(self,key:str):
        try:(self.root/Path(key).name).unlink()
        except FileNotFoundError:pass

def build_object_storage():
    if settings.object_storage_backend=="s3":
        from .s3_storage import S3ObjectStorage
        if not settings.s3_bucket: raise ValueError("AEGISMIND_S3_BUCKET is required for S3 object storage")
        return S3ObjectStorage(settings.s3_bucket,settings.s3_endpoint_url or None,settings.s3_region or None)
    return LocalObjectStorage()

object_storage=build_object_storage()
