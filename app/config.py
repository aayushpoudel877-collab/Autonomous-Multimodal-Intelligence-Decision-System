import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
load_dotenv()
class Settings(BaseModel):
    app_name:str=os.getenv("APP_NAME","AegisMind")
    log_level:str=os.getenv("LOG_LEVEL","INFO")
    llm_provider:str=os.getenv("LLM_PROVIDER","local")
    llm_api_key:str=os.getenv("LLM_API_KEY","")
    llm_model:str=os.getenv("LLM_MODEL","")
    db_path:str=os.getenv("AEGISMIND_DB_PATH","data/aegismind.db")
    storage_backend:str=os.getenv("AEGISMIND_STORAGE_BACKEND","sqlite").lower()
    postgres_url:str=os.getenv("AEGISMIND_POSTGRES_URL","")
    object_storage_dir:str=os.getenv("AEGISMIND_OBJECT_STORAGE_DIR","data/objects")
    worker_count:int=Field(default=int(os.getenv("AEGISMIND_WORKERS","2")),ge=1,le=16)
    chunk_size:int=Field(default=int(os.getenv("CHUNK_SIZE","900")),ge=100)
    chunk_overlap:int=Field(default=int(os.getenv("CHUNK_OVERLAP","120")),ge=0)
settings=Settings()
