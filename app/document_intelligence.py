import hashlib
import re
from pathlib import Path
from typing import Any
from PIL import Image
from pypdf import PdfReader
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import pytesseract
except ImportError:
    pytesseract = None
try:
    import fitz
except ImportError:
    fitz = None

def detect_language(text: str) -> str:
    if not text.strip(): return "unknown"
    nepali = len(re.findall(r"[\u0900-\u097F]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if nepali and latin: return "ne+en"
    if nepali: return "ne"
    if latin: return "en"
    return "other"

def _ocr_image(path: str, lang: str = "eng") -> str:
    if pytesseract is None: return ""
    try: return pytesseract.image_to_string(Image.open(path), lang=lang).strip()
    except Exception: return ""

def image_document(path: str, ocr: bool = True, ocr_language: str = "eng") -> dict[str, Any]:
    data = Path(path).read_bytes()
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        preview = list(rgb.resize((64, 64)).getdata())
        brightness = round(sum(sum(pixel) / 3 for pixel in preview) / len(preview), 2)
        text = _ocr_image(path, ocr_language) if ocr else ""
        return {"filename":Path(path).name,"media_type":Image.MIME.get(image.format,"image/unknown"),"width":image.width,"height":image.height,"mode":image.mode,"mean_brightness":brightness,"sha256":hashlib.sha256(data).hexdigest(),"ocr":{"enabled":ocr,"available":pytesseract is not None,"text":text,"language":detect_language(text)}}

def _page_tables(path: str, page_number: int) -> list[list[list[str]]]:
    if pdfplumber is None: return []
    try:
        with pdfplumber.open(path) as pdf:
            tables = pdf.pages[page_number-1].extract_tables() or []
            return [[[cell or "" for cell in row] for row in table] for table in tables]
    except Exception: return []

def _ocr_pdf_page(path: str, page_number: int, language: str = "eng") -> str:
    if fitz is None or pytesseract is None: return ""
    try:
        doc = fitz.open(path)
        page = doc.load_page(page_number-1)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
        image = Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
        return pytesseract.image_to_string(image,lang=language).strip()
    except Exception: return ""

def pdf_document(path: str, ocr: bool = True, ocr_language: str = "eng") -> dict[str, Any]:
    reader = PdfReader(path)
    pages=[]; total_text=[]
    for index,page in enumerate(reader.pages,start=1):
        text=(page.extract_text() or "").strip()
        extracted_by="text"
        if not text and ocr:
            text=_ocr_pdf_page(path,index,ocr_language)
            extracted_by="ocr" if text else "none"
        tables=_page_tables(path,index)
        pages.append({"page":index,"text":text,"character_count":len(text),"language":detect_language(text),"extracted_by":extracted_by,"tables":tables,"table_count":len(tables)})
        if text: total_text.append(text)
    combined="\n\n".join(total_text)
    return {"filename":Path(path).name,"media_type":"application/pdf","sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),"page_count":len(pages),"language":detect_language(combined),"ocr":{"enabled":ocr,"available":fitz is not None and pytesseract is not None,"language":ocr_language},"pages":pages}
