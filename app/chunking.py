import re
from .schemas import Source
from .config import settings

def chunk_text(text: str,size: int|None=None,overlap: int|None=None):
    size=size or settings.chunk_size; overlap=settings.chunk_overlap if overlap is None else overlap
    text=re.sub(r"\s+"," ",text).strip()
    if not text:return []
    if overlap>=size:raise ValueError("overlap must be smaller than size")
    chunks=[]; start=0
    while start<len(text):
        end=min(len(text),start+size)
        if end<len(text):
            boundary=text.rfind(". ",start,end)
            if boundary>start+size//2:end=boundary+1
        chunks.append(text[start:end].strip())
        if end==len(text):break
        start=max(start+1,end-overlap)
    return chunks

def chunk_source(source:Source):
    parts=chunk_text(source.content)
    return [Source(id=f"{source.id}:chunk:{i}",title=f"{source.title} [{i+1}/{len(parts)}]",content=p,metadata={**source.metadata,"parent_id":source.id,"chunk_index":i}) for i,p in enumerate(parts)]

def chunk_document_pages(source:Source,pages:list[dict]):
    chunks=[]
    for page in pages:
        text=page.get("text","")
        if not text.strip():continue
        page_source=Source(
            id=f"{source.id}:page:{page['page']}",
            title=f"{source.title} — Page {page['page']}",
            content=text,
            metadata={**source.metadata,"parent_id":source.id,"page":page["page"],"script":page.get("script","unknown"),"extracted_by":page.get("extracted_by","none"),"table_count":page.get("table_count",0),"modality":"document","indexed_chunk":True},
        )
        chunks.append(page_source)
    return chunks
