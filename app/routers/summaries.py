from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.rag import RAGIndex
from app.services.llm import LLM
from app.services.emailer import send_email

router = APIRouter(prefix="/api/summaries", tags=["summaries"])

@router.post("", response_model=schemas.SummaryOut)
def create_summary(payload: schemas.SummaryCreate, db: Session = Depends(get_db)):
    t = db.get(models.Transcript, payload.transcript_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transcript not found")

    rag = RAGIndex(transcript_id=t.id)
    try:
        rag.load()
    except FileNotFoundError:
        chunks = [c.content for c in t.chunks]
        if not chunks:
            raise HTTPException(status_code=400, detail="Transcript not indexed")
        rag.build(chunks)

    retrieved = rag.query(payload.instruction, k=8)
    retrieved_chunks = [c for _, _, c in retrieved]

    llm = LLM()
    content = llm.generate(payload.instruction, retrieved_chunks)

    s = models.Summary(transcript_id=t.id, instruction=payload.instruction, content=content)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

@router.get("/{summary_id}", response_model=schemas.SummaryOut)
def get_summary(summary_id: int, db: Session = Depends(get_db)):
    s = db.get(models.Summary, summary_id)
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")
    return s

@router.patch("/{summary_id}", response_model=schemas.SummaryOut)
def update_summary(summary_id: int, payload: schemas.SummaryUpdate, db: Session = Depends(get_db)):
    s = db.get(models.Summary, summary_id)
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")
    s.content = payload.content
    db.commit()
    db.refresh(s)
    return s

@router.post("/{summary_id}/share")
def share_summary(summary_id: int, payload: schemas.ShareRequest, db: Session = Depends(get_db)):
    s = db.get(models.Summary, summary_id)
    if not s:
        raise HTTPException(status_code=404, detail="Summary not found")

    subject = payload.subject or f"Meeting Summary: Transcript #{s.transcript_id}"
    message = payload.message or "Please find the meeting summary below."
    body = f"""{message}

Instruction:
{s.instruction}

Summary:
{s.content}

— Sent via Meeting Summarizer
"""
    try:
        send_email([str(r) for r in payload.recipients], subject, body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")
    return {"status": "sent", "recipients": payload.recipients}
