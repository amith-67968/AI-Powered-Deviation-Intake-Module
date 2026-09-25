from io import BytesIO
from pathlib import Path
from fastapi import HTTPException, UploadFile
from docx import Document
from pypdf import PdfReader

SUPPORTED_CONTENT_TYPES = {
    "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"
}
SUPPORTED_SUFFIXES = {".pdf", ".docx", ".txt"}


async def extract_uploaded_text(file: UploadFile, max_bytes: int) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES and (file.content_type or "") not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(415, "Unsupported file type. Upload a PDF, DOCX, or TXT file.")
    content = await file.read()
    if not content:
        raise HTTPException(422, "The uploaded document is empty.")
    if len(content) > max_bytes:
        raise HTTPException(413, "Document exceeds the configured upload limit.")
    try:
        if suffix == ".pdf" or file.content_type == "application/pdf":
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        elif suffix == ".docx":
            text = "\n".join(p.text for p in Document(BytesIO(content)).paragraphs)
        else:
            text = content.decode("utf-8", errors="replace")
    except Exception as exc:
        raise HTTPException(422, "Unable to extract text from this document.") from exc
    if not text.strip():
        raise HTTPException(422, "No readable text was found in this document.")
    return text.strip()
