from typing import Any
from pydantic import BaseModel,Field
class Source(BaseModel):
    id:str; title:str; content:str; metadata:dict[str,Any]={}
class IngestTextRequest(BaseModel):
    title:str; text:str; metadata:dict[str,Any]={}
class RetrieveRequest(BaseModel):
    query:str; top_k:int=Field(5,ge=1,le=20)
class AskRequest(BaseModel):
    question:str; top_k:int=Field(5,ge=1,le=20)
class AnomalyRequest(BaseModel):
    values:list[float]; contamination:float=Field(.05,gt=0,lt=.5)
class ForecastRequest(BaseModel):
    values:list[float]; horizon:int=Field(5,ge=1,le=100)
class DecisionRequest(BaseModel):
    question:str; signals:dict[str,Any]={}; evidence:list[str]=[]
class AgentRequest(BaseModel):
    goal:str; context:dict[str,Any]={}
class Decision(BaseModel):
    recommendation:str; confidence:float; evidence:list[str]; reasoning:list[str]; risks:list[str]