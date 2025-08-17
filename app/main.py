# app/main.py
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import transcripts, summaries

logger = structlog.get_logger(__name__)

app = FastAPI(title="Meeting Summarizer API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(transcripts.router)
app.include_router(summaries.router)

@app.get("/health")
def health():
    return {"status": "ok"}
