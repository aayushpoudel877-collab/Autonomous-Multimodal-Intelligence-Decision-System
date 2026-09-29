import uuid
from pathlib import Path
from .schemas import Source
from .store import store
from .retrieval import retriever
from .document_intelligence import pdf_document,image_document
from .chunking import chunk_document_pages
from .graph import knowledge_graph

def ingest_text(title,text,metadata=None):
    source=Source(id=str(uuid.uuid4()),title=title,content=text,metadata=metadata or {})
    store.add(source); knowledge_graph.add_text(source.id,source.content); retriever.rebuild(store.all())
    return source.model_dump()

def ingest_document(path,filename,ocr_language="eng"):
    manifest=pdf_document(path,ocr=True,ocr_language=ocr_language)
    parent=Source(id=str(uuid.uuid4()),title=filename or "document.pdf",content="",metadata={"type":"pdf","media_type":"application/pdf","sha256":manifest["sha256"],"page_count":manifest["page_count"],"script":manifest["script"],"modality":"document"})
    page_sources=chunk_document_pages(parent,manifest["pages"])
    for source in page_sources:
        store.add(source); knowledge_graph.add_text(source.id,source.content)
    retriever.rebuild(store.all())
    return {"document":parent.model_dump(),"manifest":manifest,"indexed_chunks":len(page_sources)}

def ingest_image(path,filename,ocr_language="eng"):
    analysis=image_document(path,ocr=True,ocr_language=ocr_language)
    text=analysis["ocr"]["text"]; indexed=None
    if text:
        indexed=Source(id=str(uuid.uuid4()),title=filename or "image",content=text,metadata={"type":"image","modality":"image","sha256":analysis["sha256"],"script":analysis["ocr"]["script"],"extracted_by":"ocr"})
        store.add(indexed); knowledge_graph.add_text(indexed.id,text); retriever.rebuild(store.all())
    return {"filename":filename,"analysis":analysis,"indexed_source":indexed.model_dump() if indexed else None}
