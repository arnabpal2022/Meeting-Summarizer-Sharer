from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.utils.text import chunk_text
from app.services.rag import RAGIndex
from app.utils.pdf import extract_text_from_pdf

router = APIRouter(prefix="/api/transcripts", tags=["transcripts"])

@router.post("", response_model=schemas.TranscriptOut)
def create_transcript(payload: schemas.TranscriptCreate, db: Session = Depends(get_db)):
    t = models.Transcript(title=payload.title, text=payload.text)
    db.add(t)
    db.commit()
    db.refresh(t)

    chunks = chunk_text(payload.text)
    for i, c in enumerate(chunks):
        db.add(models.TranscriptChunk(transcript_id=t.id, ordinal=i, content=c))
    db.commit()

    rag = RAGIndex(transcript_id=t.id)
    rag.build([c for c in chunks])

    return t

@router.post("/upload_pdf", response_model=schemas.TranscriptOut)
async def upload_pdf_transcript(
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".pdf") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    data = await file.read()
    text = extract_text_from_pdf(data)
    if not text or len(text.strip()) < 5:
        raise HTTPException(status_code=400, detail="No extractable text found in PDF (OCR not supported)")
    t = models.Transcript(title=title, text=text)
    db.add(t)
    db.commit()
    db.refresh(t)

    chunks = chunk_text(text)
    for i, c in enumerate(chunks):
        db.add(models.TranscriptChunk(transcript_id=t.id, ordinal=i, content=c))
    db.commit()

    rag = RAGIndex(transcript_id=t.id)
    rag.build([c for c in chunks])

    return t

@router.get("/{transcript_id}", response_model=schemas.TranscriptOut)
def get_transcript(transcript_id: int, db: Session = Depends(get_db)):
    t = db.get(models.Transcript, transcript_id)
    if not t:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return t
