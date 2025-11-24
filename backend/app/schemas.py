# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# ----- Auth -----
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# ----- Project / Sections -----
class SectionCreate(BaseModel):
    title: str
    order: int

class SectionOut(BaseModel):
    id: int
    title: str
    order: int
    content: Optional[str]

    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    title: str
    topic: str
    doc_type: str  # "docx" or "pptx"
    sections: List[SectionCreate]

class ProjectOut(BaseModel):
    id: int
    title: str
    topic: str
    doc_type: str
    created_at: datetime
    sections: List[SectionOut]

    class Config:
        orm_mode = True

# ----- Refinement -----
class RefinementRequest(BaseModel):
    prompt: str

class FeedbackRequest(BaseModel):
    liked: bool

class CommentRequest(BaseModel):
    text: str
