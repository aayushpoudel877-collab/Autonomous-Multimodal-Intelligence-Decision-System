from pypdf import PdfReader
from PIL import Image
import hashlib
from pathlib import Path
def text_from_pdf(path): return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages).strip()
def image_analysis(path):
    im=Image.open(path).convert("RGB"); px=list(im.resize((64,64)).getdata())
    return {"format":Image.open(path).format,"width":im.width,"height":im.height,"mode":im.mode,"mean_brightness":round(sum(sum(p)/3 for p in px)/len(px),2),"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest()}