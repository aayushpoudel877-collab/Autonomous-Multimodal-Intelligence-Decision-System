from .document_intelligence import image_document, pdf_document

def text_from_pdf(path): return "\n\n".join(page["text"] for page in pdf_document(path,ocr=False)["pages"] if page["text"]).strip()

def image_analysis(path): return image_document(path,ocr=False)
