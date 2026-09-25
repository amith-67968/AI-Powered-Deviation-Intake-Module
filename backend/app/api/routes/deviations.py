import logging
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from app.ai.prompts import CHAT_PROMPT
from app.core.config import get_settings
from app.db.session import get_db
from app.graph.deviation_graph import run_deviation_graph
from app.schemas.deviation import (AnalysisResponse, ChatRequest, ChatResponse, DeviationCreate, DeviationRead, DeviationUpdate)
from app.services.deviation_service import create_deviation, delete_deviation, get_deviation, list_deviations, update_deviation
from app.utils.document_parser import extract_uploaded_text

router = APIRouter(prefix="/api/deviations", tags=["deviations"])
logger = logging.getLogger(__name__)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_deviation(text: str | None = Form(default=None), file: UploadFile | None = File(default=None)):
    if not text and not file:
        raise HTTPException(422, "Provide pasted deviation text or a supporting document.")
    if file:
        document_text = await extract_uploaded_text(file, get_settings().max_upload_mb * 1024 * 1024)
        text = f"{text.strip()}\n\n{document_text}" if text and text.strip() else document_text
    if not text or not text.strip():
        raise HTTPException(422, "Deviation text is empty.")
    if len(text) > get_settings().max_input_chars:
        raise HTTPException(413, "The supplied content is too large to analyze. Please upload or paste the relevant deviation section only.")
    try:
        return await run_deviation_graph(text)
    except RuntimeError as exc:
        logger.exception("Analysis unavailable")
        status = 503 if "not configured" in str(exc).lower() else 502
        raise HTTPException(status, "Unable to analyze the document. Please try again.") from exc


@router.post("/chat", response_model=ChatResponse)
async def deviation_chat(payload: ChatRequest):
    settings = get_settings()
    if not settings.groq_api_key:
        raise HTTPException(503, "AI assistant is not configured.")
    try:
        response = await ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0).ainvoke(
            CHAT_PROMPT.format(context=payload.deviation_context, question=payload.question)
        )
        return ChatResponse(answer=response.content)
    except Exception as exc:
        logger.exception("Assistant chat failed")
        raise HTTPException(502, "Unable to answer the question. Please try again.") from exc


@router.post("", response_model=DeviationRead, status_code=201)
def save_deviation(payload: DeviationCreate, db: Session = Depends(get_db)):
    try:
        return create_deviation(db, payload)
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to save deviation")
        raise HTTPException(500, "Unable to save the deviation. Please try again.") from exc


@router.get("", response_model=list[DeviationRead])
def all_deviations(q: str | None = None, db: Session = Depends(get_db)):
    return list_deviations(db, q)


@router.get("/{deviation_id}", response_model=DeviationRead)
def one_deviation(deviation_id: int, db: Session = Depends(get_db)):
    record = get_deviation(db, deviation_id)
    if not record:
        raise HTTPException(404, "Deviation not found.")
    return record


@router.put("/{deviation_id}", response_model=DeviationRead)
def edit_deviation(deviation_id: int, payload: DeviationUpdate, db: Session = Depends(get_db)):
    record = get_deviation(db, deviation_id)
    if not record:
        raise HTTPException(404, "Deviation not found.")
    return update_deviation(db, record, payload)


@router.delete("/{deviation_id}", status_code=204)
def remove_deviation(deviation_id: int, db: Session = Depends(get_db)):
    record = get_deviation(db, deviation_id)
    if not record:
        raise HTTPException(404, "Deviation not found.")
    delete_deviation(db, record)
