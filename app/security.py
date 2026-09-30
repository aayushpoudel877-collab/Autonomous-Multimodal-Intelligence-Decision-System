import secrets
from fastapi import Header,HTTPException
from .config import settings

def verify_api_key(api_key:str|None=Header(default=None,alias="X-API-Key")):
    if not settings.api_keys:return {"role":"admin","authenticated":False}
    if not api_key:raise HTTPException(401,"API key required")
    for item in settings.api_keys.split(","):
        key,_,role=item.partition(":")
        if secrets.compare_digest(key,api_key):
            return {"role":role or "reader","authenticated":True}
    raise HTTPException(403,"Invalid API key")
