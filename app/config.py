import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()
class Settings(BaseModel):
    app_name:str=os.getenv("APP_NAME","AegisMind")
    log_level:str=os.getenv("LOG_LEVEL","INFO")
    llm_provider:str=os.getenv("LLM_PROVIDER","local")
    llm_api_key:str=os.getenv("LLM_API_KEY","")
    llm_model:str=os.getenv("LLM_MODEL","")
    db_path:str=os.getenv("AEGISMIND_DB_PATH","data/aegismind.db")
    chunk_size:int=int(os.getenv("CHUNK_SIZE","900"))
    chunk_overlap:int=int(os.getenv("CHUNK_OVERLAP","120"))
settings=Settings()
