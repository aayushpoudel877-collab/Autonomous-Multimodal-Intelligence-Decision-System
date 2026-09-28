import re
from .schemas import Source

def chunk_text(text: str,size: int=900,overlap: int=120):
    text=re.sub(r"\s+"," ",text).strip()
    if not text: return []
    if overlap>=size: raise ValueError("overlap must be smaller than size")
    chunks=[]; start=0
    while start<len(text):
        end=min(len(text),start+size)
        if end<len(text):
            boundary=text.rfind(". ",start,end)
            if boundary>start+size//2: end=boundary+1
        chunks.append(text[start:end].strip())
        if end==len(text): break
        start=max(start+1,end-overlap)
    return chunks

def chunk_source(source: Source):
    parts=chunk_text(source.content)
    return [Source(id=f"{source.id}:chunk:{i}",title=f"{source.title} [{i+1}/{len(parts)}]",content=p,metadata={**source.metadata,"parent_id":source.id,"chunk_index":i}) for i,p in enumerate(parts)]

def chunk_document_pages(source: Source,pages:list[dict],size:int=900,overlap:int=120):
    chunks=[]
    for page in pages:
        page_source=Source(id=f"{source.id}:page:{page['page']}",title=f"{source.title} — Page {page['page']}",content=page.get("text",""),metadata={**source.metadata,"parent_id":source.id,"page":page["page"],"script":page.get("script","unknown"),"extracted_by":page.get("extracted_by","none"),"table_count":page.get("table_count",0),"modality":"document"})
        chunks.extend(chunk_source(page_source))
    return chunks
