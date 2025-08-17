from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class TranscriptCreate(BaseModel):
    title: str = Field(..., max_length=255)
    text: str = Field(..., min_length=1)

class TranscriptOut(BaseModel):
    id: int
    title: str
    text: str
    class Config:
        from_attributes = True

class SummaryCreate(BaseModel):
    transcript_id: int
    instruction: str = Field(..., min_length=3, max_length=4000)

class SummaryOut(BaseModel):
    id: int
    transcript_id: int
    instruction: str
    content: str
    class Config:
        from_attributes = True

class SummaryUpdate(BaseModel):
    content: str = Field(..., min_length=1)

class ShareRequest(BaseModel):
    recipients: List[EmailStr]
    subject: Optional[str] = None
    message: Optional[str] = None
