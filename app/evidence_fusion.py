from collections import defaultdict
MODALITY_PRIORS={"text":1.0,"document":1.05,"image":0.9,"table":1.05}

def fuse_evidence(results,limit=8):
    grouped=defaultdict(lambda:{"source":None,"score":0.0,"modalities":set(),"signals":[]})
    for item in results:
        source=item["source"]; modality=source.metadata.get("modality",source.metadata.get("type","text"))
        score=float(item.get("score",0.0))*MODALITY_PRIORS.get(modality,1.0)
        row=grouped[source.id]; row["source"]=source; row["score"]=max(row["score"],score)
        row["modalities"].add(modality); row["signals"].append({"modality":modality,"score":round(score,4)})
    fused=[]
    for row in grouped.values():
        bonus=0.08 if len(row["modalities"])>1 else 0.0
        fused.append({"source":row["source"],"score":round(min(1.0,row["score"]+bonus),4),"modalities":sorted(row["modalities"]),"signals":row["signals"]})
    return sorted(fused,key=lambda x:x["score"],reverse=True)[:limit]
