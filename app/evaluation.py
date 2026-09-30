import math
from dataclasses import dataclass
from .retrieval import retriever

@dataclass
class RetrievalQuery:
    query:str
    relevant_ids:list[str]

def reciprocal_rank(results,relevant):
    for i,item in enumerate(results,1):
        if item["source"].id in relevant:return 1.0/i
    return 0.0

def recall_at_k(results,relevant,k):
    relevant=set(relevant)
    if not relevant:return 0.0
    found={x["source"].id for x in results[:k]}
    return len(found&relevant)/len(relevant)

def ndcg_at_k(results,relevant,k):
    relevant=set(relevant)
    gains=[1.0 if x["source"].id in relevant else 0.0 for x in results[:k]]
    dcg=sum(g/math.log2(i+2) for i,g in enumerate(gains))
    ideal=sum(1.0/math.log2(i+2) for i in range(min(k,len(relevant))))
    return dcg/ideal if ideal else 0.0

def evaluate(queries:list[RetrievalQuery],k:int=5):
    rows=[]
    for item in queries:
        results=retriever.search(item.query,k)
        rows.append({"query":item.query,"recall_at_k":recall_at_k(results,item.relevant_ids,k),"mrr":reciprocal_rank(results,set(item.relevant_ids)),"ndcg_at_k":ndcg_at_k(results,item.relevant_ids,k)})
    n=len(rows)
    if not n:return {"count":0,"k":k,"recall_at_k":0.0,"mrr":0.0,"ndcg_at_k":0.0,"queries":[]}
    return {"count":n,"k":k,"recall_at_k":round(sum(x["recall_at_k"] for x in rows)/n,4),"mrr":round(sum(x["mrr"] for x in rows)/n,4),"ndcg_at_k":round(sum(x["ndcg_at_k"] for x in rows)/n,4),"queries":rows}
